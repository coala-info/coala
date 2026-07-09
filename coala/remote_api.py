from fastapi import FastAPI, UploadFile, Body
from pydantic import create_model, Field, ConfigDict
import logging
import uvicorn
from tempfile import NamedTemporaryFile, mkdtemp
from cwltool import factory
from cwltool.context import RuntimeContext
from threading import Thread
import time
from typing import Optional, List
from coala.tool_logic import run_tool  # <-- import shared logic


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# ponytail: pydantic forbids these as field names; alias + by_alias keeps CWL ids intact
_PYDANTIC_RESERVED_FIELDS = frozenset({'model_config'})


def _pydantic_field_name(cwl_name: str) -> str:
    return f'{cwl_name}_' if cwl_name in _PYDANTIC_RESERVED_FIELDS else cwl_name


class tool_api():
    def __init__(self, cwl_file, tool_name='tool', host='0.0.0.0', port=8000, read_outs=False):
        """
        Initializes a tool_api object, which is used to create a FastAPI server for a given CWL file.

        Parameters:
            cwl_file (str): The path to the CWL file.
            tool_name (str): The name of the tool. Defaults to 'tool'.
            host (str): The host IP address. Defaults to '0.0.0.0'.
            port (int): The port number. Defaults to 8000.
            read_outs (bool): Whether to read the outputs. Defaults to False.

        Returns:
            None
        """
        self.cwl_file = cwl_file
        self.tool_name = tool_name
        self.host = host
        self.port = port
        self.read_outs = read_outs
        self.server = None
        self.url = None
        # cwl
        runtime_context = RuntimeContext()
        runtime_context.outdir = mkdtemp()
        fac = factory.Factory(runtime_context=runtime_context)
        self.tool = fac.make(cwl_file)

        self.inputs = self.tool.t.inputs_record_schema['fields']
        self.outputs = self.tool.t.outputs_record_schema['fields']

        # map types
        it_map = {}
        for it in self.inputs:
            # it['type'] can be a list like ['null', 'org.w3id.cwl.cwl.File']
            type_list = it['type'] if isinstance(it['type'], list) else [it['type']]
            type_str = ' '.join(str(t) for t in type_list)  # Join for checking substrings
            cwl_name = it['name']
            field_name = _pydantic_field_name(cwl_name)

            if 'File' in type_str:
                py_type, default = str, None
            elif 'string' in type_str:
                py_type, default = str, None
            elif 'double' in type_str:
                py_type, default = float, None
            elif 'int' in type_str:
                py_type, default = int, None
            elif 'boolean' in type_str:
                py_type, default = bool, None
            else:
                py_type, default = str, None

            if 'null' in type_list:
                py_type = Optional[py_type]

            if field_name != cwl_name:
                it_map[field_name] = (py_type, Field(default=default, alias=cwl_name))
            else:
                it_map[field_name] = (py_type, default)

        create_kwargs = {}
        if any(it['name'] in _PYDANTIC_RESERVED_FIELDS for it in self.inputs):
            create_kwargs['__config__'] = ConfigDict(populate_by_name=True)
        self.Base = create_model('Base', **create_kwargs, **it_map)

        # define tool
        # fastapi
        self.app = FastAPI()

        @self.app.post('/uploadFile/')
        async def uploadFile(file: UploadFile):
            with NamedTemporaryFile(delete=False) as tmp:
                contents = file.file.read()
                tmp.write(contents)
            return {"filename": file.filename, "filepath": tmp.name}

        @self.app.post(f"/{self.tool_name}/")  
        def tool(data: List[self.Base] = Body(...)):
            logger.info(data)
            params = data[0].model_dump(by_alias=True)
            outs = run_tool(self.tool, params, self.outputs, self.read_outs)
            logger.info(outs)
            return outs

    def serve(self):
        """
        Starts a FastAPI server to serve the specified tool.

        This function initializes a FastAPI server and sets up the necessary routes for the specified tool. The server listens for HTTP requests on the specified host and port.
        """
        config = uvicorn.Config(app=self.app, host=self.host, port=self.port)
        self.server = uvicorn.Server(config=config)
        thread = Thread(target=self.server.run)
        thread.start()  # non-blocking call

        while not self.server.started:
            time.sleep(0.1)
        else:
            print(f"HTTP server is now running on http://{self.host}:{self.port}")
            self.url = f"http://{self.host}:{self.port}/{self.tool_name}/"

    
    def stop(self):
        """
        Stops the server by setting the should_exit flag to True.
        """
        self.server.should_exit = True



# api = tool_api(cwl_file='test_data/dockstore-tool-md5sum.cwl')
# api.serve()
# api.stop()