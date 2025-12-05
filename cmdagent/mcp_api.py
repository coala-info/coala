from fastapi import FastAPI, UploadFile, Body, File
from pydantic import create_model
import logging
import uvicorn
from tempfile import NamedTemporaryFile, mkdtemp
from cwltool import factory
from cwltool.context import RuntimeContext
from threading import Thread
import time
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from cmdagent.tool_logic import run_tool  # <-- import shared logic
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class mcp_api():
    def __init__(self, host='0.0.0.0', port=8000):
        """
        Initializes an MCP server that can host multiple CWL tools.

        Parameters:
            host (str): The host IP address. Defaults to '0.0.0.0'.
            port (int): The port number. Defaults to 8000.
            read_outs (bool): Whether to read the outputs. Defaults to True.
        """
        self.host = host
        self.port = port
        self.server = None
        self.url = None
        self.mcp = FastMCP(host=host, port=port)
        self.tools = {}  # tool_name -> tool info
        self.system_prompt = """
At the end of your response, append a summary listing the tool name and version from the tool's description using this exact format:
```
Tool Invocation Summary:
tool_name: <TOOL_NAME>
tool_version: <TOOL_VERSION>
```
"""
    

        @self.mcp.tool()
        async def uploadFile(file: UploadFile = File(description="The file to be uploaded to the server")) -> dict:
            """
            Upload a file to the server.
            """
            with NamedTemporaryFile(delete=False) as tmp:
                contents = file.file.read()
                tmp.write(contents)
            return {"filename": file.filename, "filepath": tmp.name}

    def add_tool(self, cwl_file, tool_name, read_outs=True):
        """
        Adds a CWL tool to the MCP server.
        """
        runtime_context = RuntimeContext()
        runtime_context.outdir = mkdtemp()
        fac = factory.Factory(runtime_context=runtime_context)
        tool = fac.make(cwl_file)

        inputs = tool.t.inputs_record_schema['fields']
        outputs = tool.t.outputs_record_schema['fields']

        # map types
        it_map = {}
        for it in inputs:
            # it['type'] can be a list like ['null', 'org.w3id.cwl.cwl.File']
            type_list = it['type'] if isinstance(it['type'], list) else [it['type']]
            type_str = ' '.join(type_list)  # Join for checking substrings
            
            if 'File' in type_str:
                it_map[it['name']] = (str, None)
            elif 'string' in type_str:
                it_map[it['name']] = (str, None)
            elif 'double' in type_str:
                it_map[it['name']] = (float, None)
            else:
                it_map[it['name']] = (str, None)

            if 'null' in type_list:
                type, v = it_map[it['name']]
                it_map[it['name']] = (Optional[type], v)

        Base = create_model(f'Base_{tool_name}', **it_map)

        fields_desc = "\n\n".join(
            f"{k}: {inputs[i].get('doc', '')}, {v.annotation.__name__ if hasattr(v.annotation, '__name__') else str(v.annotation)}"
            for i, (k, v) in enumerate(Base.model_fields.items())
        )

        # Extract Docker image information
        docker_info = ""
        # Check requirements first
        if hasattr(tool.t, 'requirements') and tool.t.requirements:
            for req in tool.t.requirements:
                if isinstance(req, dict) and req.get('class') == 'DockerRequirement':
                    docker_pull = req.get('dockerPull', '')
                    if docker_pull:
                        docker_info = f"\n\ntool_version: {docker_pull}"
                        break
        # If not found in requirements, check hints
        if not docker_info and hasattr(tool.t, 'hints') and tool.t.hints:
            for hint in tool.t.hints:
                if isinstance(hint, dict) and hint.get('class') == 'DockerRequirement':
                    docker_pull = hint.get('dockerPull', '')
                    if docker_pull:
                        docker_info = f"\n\ntool_version: {docker_pull}"
                        break

        tool_desc = f"{tool_name}: {tool.t.tool.get('label', '')}\n\n {tool.t.tool.get('doc', '')}{docker_info}"

        @self.mcp.tool(name=tool_name, description=tool_desc)
        def mcp_tool(
            data: List[Base] = Body(
                ...,
                description=f"Input data for '{tool_name}'. Fields: \n\n{fields_desc}"
            )
        ) -> dict:
            logger.info(data)
            params = data[0].model_dump()
            outs = run_tool(tool, params, outputs, read_outs)
            logger.info(outs)

            return str(outs) + "\n\n" + self.system_prompt

        # Store tool info if needed
        self.tools[tool_name] = {
            'cwl_file': cwl_file,
            'tool': tool,
            'Base': Base,
            'inputs': inputs,
            'outputs': outputs
        }

    def serve(self):
        print(f"Starting MCP server at http://{self.host}:{self.port}/", flush=True)
        self.mcp.run(transport='streamable-http')
        # thread = threading.Thread(target=self.mcp.run, kwargs={'transport': 'sse'}, daemon=True)
        # thread.start()
        # self.server_thread = thread
