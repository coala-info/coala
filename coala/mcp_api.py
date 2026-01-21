from fastapi import FastAPI, UploadFile, File
from pydantic import create_model, Field
import logging
import uvicorn
from tempfile import NamedTemporaryFile, mkdtemp
from cwltool import factory
from cwltool.context import RuntimeContext
from threading import Thread
import time
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from coala.tool_logic import run_tool  # <-- import shared logic
import threading
import sys
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Use stderr for logging to avoid interfering with stdio transport
logger.addHandler(logging.StreamHandler(sys.stderr))


class mcp_api():
    def __init__(self, host='0.0.0.0', port=8000):
        """
        Initializes an MCP server that can host multiple CWL tools.

        Parameters:
            host (str): The host IP address. Defaults to '0.0.0.0'.
            port (int): The port number. Defaults to 8000.

        Notes:
            Output-reading behavior is controlled per tool via `add_tool(..., read_outs=False)`.
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
    

        # @self.mcp.tool()
        # async def uploadFile(file: UploadFile = File(description="The file to be uploaded to the server")) -> dict:
        #     """
        #     Upload a file to the server.
        #     """
        #     with NamedTemporaryFile(delete=False) as tmp:
        #         contents = file.file.read()
        #         tmp.write(contents)
        #     return {"filename": file.filename, "filepath": tmp.name}

    def _build_field_description(self, field_name, input_field, model_field):
        """
        Build field description with type hints.
        """
        doc = input_field.get('doc', '')
        type_val = input_field.get('type', '')
        type_list = type_val if isinstance(type_val, list) else [type_val]
        type_str = ' '.join(str(t) for t in type_list)
        
        type_hint = ""
        if 'File' in type_str:
            type_hint = "file path"
        elif 'string' in type_str:
            type_hint = "str"
        elif 'double' in type_str or 'float' in type_str:
            type_hint = "float"
        elif 'int' in type_str:
            type_hint = "int"
        elif 'boolean' in type_str:
            type_hint = "bool"
        
        annotation = model_field.annotation.__name__ if hasattr(model_field.annotation, '__name__') else str(model_field.annotation)
        
        if type_hint:
            return f"{field_name}: {doc}, {annotation}, {type_hint}"
        else:
            return f"{field_name}: {doc}, {annotation}"

    def _build_output_description(self, output_field):
        """
        Build output field description with type hints.
        """
        field_name = output_field.get('name', '')
        doc = output_field.get('doc', '')
        type_val = output_field.get('type', '')
        type_list = type_val if isinstance(type_val, list) else [type_val]
        type_str = ' '.join(str(t) for t in type_list)
        
        type_hint = ""
        if 'File' in type_str:
            type_hint = "file path"
        elif 'string' in type_str:
            type_hint = "str"
        elif 'double' in type_str or 'float' in type_str:
            type_hint = "float"
        elif 'int' in type_str:
            type_hint = "int"
        elif 'boolean' in type_str:
            type_hint = "bool"
        
        if type_hint:
            return f"{field_name}: {doc}, {type_hint}"
        else:
            return f"{field_name}: {doc}"

    def _transform_input_value(self, field_name, value, input_type):
        """
        Transform input values based on their expected type.
        
        - For File types: If value is just a filename, try to resolve to full path
        - For string types: If value is a full path, extract just the filename
        - For array types: Transform each element in the array
        
        Parameters:
            field_name: Name of the input field
            value: The input value to transform
            input_type: The CWL type definition for this input
        
        Returns:
            Transformed value
        """
        if value is None:
            return value
        
        # Check if it's an array type
        is_array = False
        base_type = input_type
        
        if isinstance(input_type, list):
            # Filter out 'null' to get actual types
            non_null_types = [t for t in input_type if t != 'null']
            if non_null_types:
                base_type = non_null_types[0]
        
        # Check for array notation (e.g., 'float[]' or {'type': 'array', 'items': 'float'})
        if isinstance(base_type, dict) and base_type.get('type') == 'array':
            is_array = True
            base_type = base_type.get('items', 'string')
        elif isinstance(base_type, str) and '[]' in base_type:
            is_array = True
            base_type = base_type.replace('[]', '')
        
        # If value is a list and type is array, transform each element
        if is_array and isinstance(value, list):
            return [self._transform_input_value(f"{field_name}[{i}]", item, base_type) 
                    for i, item in enumerate(value)]
        
        # Convert type to string for checking
        type_str = str(base_type) if not isinstance(base_type, dict) else base_type.get('type', '')
        
        # Check if it's a File type
        if 'File' in type_str and isinstance(value, str):
            # If it's already a file:// URI, return as is
            if value.startswith('file://'):
                return value
            
            # If it's already an absolute path that exists, return as is
            if os.path.isabs(value) and os.path.isfile(value):
                return value
            
            # Try to resolve filename to full path
            # Check if it's a file in current directory
            if os.path.isfile(value):
                return os.path.abspath(value)
            
            # Check in current working directory
            cwd_path = os.path.join(os.getcwd(), value)
            if os.path.isfile(cwd_path):
                return os.path.abspath(cwd_path)
            
            # If not found, return as is (let run_tool handle it)
            return value
        
        # Check if it's a string type
        elif 'string' in type_str and isinstance(value, str):
            # If it looks like a full path, check if directory exists
            if os.path.sep in value or (os.path.altsep and os.path.altsep in value):
                # Get the directory part of the path
                dir_path = os.path.dirname(value)
                # Only extract filename if the directory exists
                if dir_path and os.path.isdir(dir_path):
                    # Extract filename from path
                    filename = os.path.basename(value)
                    logger.info(f"Transformed string input '{field_name}': '{value}' -> '{filename}'")
                    return filename
                # If directory doesn't exist, keep the full path as is
                return value
        
        return value

    def add_tool(self, cwl_file, tool_name=None, read_outs=False):
        """
        Adds a CWL tool to the MCP server.
        
        Parameters:
            cwl_file: Path to the CWL tool file
            tool_name: Optional tool name. If not provided, will use:
                      1. The 'id' field from the CWL tool
                      2. If 'id' is not defined, the basename of cwl_file (without .cwl extension)
            read_outs: Whether to read output files
        
        Raises:
            FileNotFoundError: If the CWL file does not exist
            Exception: If there's an error loading the CWL tool
        """
        # Check if file exists
        if not os.path.exists(cwl_file):
            raise FileNotFoundError(f"CWL file not found: {cwl_file}")
        
        if not os.path.isfile(cwl_file):
            raise ValueError(f"Path is not a file: {cwl_file}")
        
        runtime_context = RuntimeContext()
        runtime_context.outdir = mkdtemp()
        fac = factory.Factory(runtime_context=runtime_context)
        
        try:
            tool = fac.make(cwl_file)
        except Exception as e:
            raise Exception(f"Failed to load CWL tool from {cwl_file}: {str(e)}") from e
        
        # Determine tool_name if not provided
        if tool_name is None:
            # Try to get 'id' from CWL tool
            tool_id = tool.t.tool.get('id') if hasattr(tool.t, 'tool') and tool.t.tool else None
            # Only use id if it contains a '#' fragment (e.g., "file://path#ToolName")
            # If id is just a file:// path without fragment, treat it as undefined
            if tool_id and '#' in tool_id:
                tool_name = tool_id.split('#')[-1]
            # If 'id' is not defined or doesn't have a fragment, use basename of cwl_file without .cwl extension
            if not tool_name:
                tool_name = os.path.basename(cwl_file).replace('.cwl', '')

        inputs = tool.t.inputs_record_schema['fields']
        outputs = tool.t.outputs_record_schema['fields']

        # Create a mapping from field name to input field definition
        inputs_by_name = {it['name']: it for it in inputs}

        # map types
        it_map = {}
        for it in inputs:
            # it['type'] can be a list like ['null', 'org.w3id.cwl.cwl.File'] or ['null', 'float[]']
            # or a dict like {'type': 'array', 'items': 'float'}
            # or a string like 'float[]'
            raw_type = it['type']
            type_list = raw_type if isinstance(raw_type, list) else [raw_type]
            
            # Check for 'null' in type list (optional field)
            is_optional = 'null' in type_list
            # Filter out 'null' to get the actual type(s)
            non_null_types = [t for t in type_list if t != 'null']
            
            # Check if it's a dict-based array type (e.g., {'type': 'array', 'items': 'float'})
            is_array = False
            base_type_str = None
            if isinstance(raw_type, dict) and raw_type.get('type') == 'array':
                is_array = True
                items_type = raw_type.get('items', 'string')
                base_type_str = str(items_type) if not isinstance(items_type, dict) else items_type.get('type', 'string')
            elif non_null_types:
                # Check for array notation in string (e.g., 'float[]')
                # Look through non-null types for array notation
                for t in non_null_types:
                    t_str = str(t)
                    if '[]' in t_str:
                        is_array = True
                        base_type_str = t_str.replace('[]', '')
                        break
                
                if not is_array and non_null_types:
                    # Not an array, use the first non-null type
                    base_type_str = str(non_null_types[0])
            else:
                # Fallback to string if no types found
                base_type_str = 'string'
            
            # Get field description from CWL input
            field_doc = it.get('doc', '')
            
            # Determine base Python type
            if 'File' in base_type_str:
                base_py_type = str
            elif 'string' in base_type_str:
                base_py_type = str
            elif 'double' in base_type_str or 'float' in base_type_str:
                base_py_type = float
            elif 'int' in base_type_str:
                base_py_type = int
            elif 'boolean' in base_type_str:
                base_py_type = bool
            else:
                base_py_type = str

            # Wrap in List if it's an array
            if is_array:
                py_type = List[base_py_type]
            else:
                py_type = base_py_type

            # Make optional if 'null' was in type list
            if is_optional:
                py_type = Optional[py_type]
            
            # Create Field with description
            it_map[it['name']] = (py_type, Field(default=None, description=field_doc))

        Base = create_model(f'Base_{tool_name}', **it_map)

        fields_desc = "\n\n".join(
            self._build_field_description(k, inputs_by_name[k], v)
            for k, v in Base.model_fields.items()
        )

        outputs_desc = "\n\n".join(
            self._build_output_description(out)
            for out in outputs
        )

        # Extract Docker image information
        docker_info = ""
        docker_version = ""
        # Check requirements first
        if hasattr(tool.t, 'requirements') and tool.t.requirements:
            for req in tool.t.requirements:
                if isinstance(req, dict) and req.get('class') == 'DockerRequirement':
                    docker_pull = req.get('dockerPull', '')
                    if docker_pull:
                        docker_info = f"\n\ntool_version: {docker_pull}"
                        docker_version = docker_pull
                        break
        # If not found in requirements, check hints
        if not docker_info and hasattr(tool.t, 'hints') and tool.t.hints:
            for hint in tool.t.hints:
                if isinstance(hint, dict) and hint.get('class') == 'DockerRequirement':
                    docker_pull = hint.get('dockerPull', '')
                    if docker_pull:
                        docker_info = f"\n\ntool_version: {docker_pull}"
                        docker_version = docker_pull
                        break

        tool_desc = f"{tool_name}: {tool.t.tool.get('label', '')}\n\n {tool.t.tool.get('doc', '')}{docker_info}\n\nReturns:\n\n{outputs_desc}"

        @self.mcp.tool(name=tool_name, description=f"{tool_desc}\n\nInput data for '{tool_name}'. Fields: \n\n{fields_desc}")
        def mcp_tool(data: List[Base]) -> dict:
            """MCP tool wrapper for CWL tool execution."""
            # Store fields_desc as function attribute for programmatic access
            mcp_tool.fields_desc = fields_desc
            # Assign interpolated docstring with field descriptions
            mcp_tool.__doc__ = f"""
            MCP tool wrapper for CWL tool execution.
            
            Input fields:
            {fields_desc}
            """
            logger.info(data)
            params = data[0].model_dump()
            
            # Transform input values based on their types
            # Create a mapping from field name to input type
            inputs_by_name = {it['name']: it for it in inputs}
            for field_name, value in params.items():
                if field_name in inputs_by_name:
                    input_field = inputs_by_name[field_name]
                    input_type = input_field.get('type', 'string')
                    transformed_value = self._transform_input_value(field_name, value, input_type)
                    if transformed_value != value:
                        logger.info(f"Transformed input '{field_name}': '{value}' -> '{transformed_value}'")
                    params[field_name] = transformed_value
            
            outs = run_tool(tool, params, outputs, read_outs)
            outs['tool_name'] = tool_name
            outs['tool_version'] = docker_version
            outs['system_prompt'] = self.system_prompt
            logger.info(outs)
            return outs

        # Store tool info if needed
        self.tools[tool_name] = {
            'cwl_file': cwl_file,
            'tool': tool,
            'Base': Base,
            'inputs': inputs,
            'outputs': outputs
        }

    def serve(self, transport=None):
        """
        Starts the MCP server.
        
        Parameters:
            transport (str, optional): Transport type ('stdio' or 'streamable-http').
                                     If None, auto-detects based on stdin availability.
        """
        # Auto-detect transport: if stdin is not a TTY, use stdio transport
        if transport is None:
            if not sys.stdin.isatty():
                transport = 'stdio'
            else:
                transport = 'streamable-http'
        
        if transport == 'streamable-http':
            # Print to stderr to avoid interfering with stdio transport
            print(f"Starting MCP server at http://{self.host}:{self.port}/", file=sys.stderr, flush=True)
        else:
            # For stdio transport, don't print startup messages to stdout
            logger.info("Starting MCP server with stdio transport")
        
        self.mcp.run(transport=transport)
        # thread = threading.Thread(target=self.mcp.run, kwargs={'transport': 'sse'}, daemon=True)
        # thread.start()
        # self.server_thread = thread
