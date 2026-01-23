# coala/tool_logic.py
import os.path
import gzip
from cwltool.context import RuntimeContext

def configure_container_runner(runtime_context: RuntimeContext, container_runner: str) -> None:
    """
    Configure the runtime context with the specified container runner.
    
    Parameters:
        runtime_context: The RuntimeContext to configure
        container_runner: Container runtime to use ('docker', 'podman', 'singularity', 'udocker', etc.)
    """
    runtime_context.default_container = container_runner
    # Set boolean flags for specific container runners
    runtime_context.singularity = (container_runner == 'singularity')
    runtime_context.podman = (container_runner == 'podman')

def _read_file_content(filepath):
    """Read file content, handling gzipped files."""
    try:
        if filepath.endswith('.gz'):
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                return f.read().replace('\n', '')
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().replace('\n', '')
    except (UnicodeDecodeError, OSError):
        # If reading fails (binary file, etc.), return the filepath instead
        return filepath

def run_tool(tool, params, outputs, read_outs=False, container_runner=None):
    """
    Execute a CWL tool with the given parameters.
    
    Parameters:
        tool: The CWL tool object (created via factory.Factory().make())
        params: Dictionary of input parameters
        outputs: List of output field definitions
        read_outs: Whether to read output file contents (default: False)
        container_runner: Container runtime to use (default: None, uses tool's default)
                         Valid values: 'docker', 'podman', 'singularity', 'udocker', etc.
    
    Returns:
        Dictionary mapping output field names to their values
    """
    # Prepare params for CWL tool
    inputs = tool.t.inputs_record_schema['fields']
    in_dict = {}
    for i in inputs:
        in_dict[i['name']] = i['type']

    for k, v in params.items():
        if k in in_dict:
            type_val = in_dict[k]
            # Handle both list and string types (e.g., ['null', 'File'] or 'File?')
            # Convert each item to str to handle CommentedMap from ruamel.yaml (enum types)
            type_str = ' '.join(str(t) for t in type_val) if isinstance(type_val, list) else str(type_val)
            if 'File' in type_str and v is not None:
                if type(v) is dict and 'location' in v:
                    location = v['location']
                elif isinstance(v, str) and v.startswith('file://'):
                    location = v
                elif isinstance(v, str) and os.path.isfile(v):
                    location = f"file://{v}"
                else:
                    continue  # Do nothing if v is not a file
                
                params[k] = {
                    "class": "File",
                    "location": location
                }
    
    # Modify the tool's runtime context if container runner is specified
    if container_runner:
        # Try to get the original runtime context from the tool
        original_runtime_context = None
        if hasattr(tool, 'runtime_context'):
            original_runtime_context = tool.runtime_context
        elif hasattr(tool, 't') and hasattr(tool.t, 'runtime_context'):
            original_runtime_context = tool.t.runtime_context
        
        # If we found the runtime context, modify it in place
        if original_runtime_context:
            configure_container_runner(original_runtime_context, container_runner)
    
    # Execute tool (no need to pass runtime_context if we modified it in place)
    res = tool(**params)
    outs = {}
    for ot in outputs:
        out_content = res[ot['name']]
        # Handle both list and string types (e.g., ['null', 'File'] or 'File?')
        # Convert each item to str to handle CommentedMap from ruamel.yaml (enum types)
        type_val = ot['type']
        type_str = ' '.join(str(t) for t in type_val) if isinstance(type_val, list) else str(type_val)
        if read_outs and 'File' in type_str:
            # Handle both single File and File[] (array) outputs
            file_result = res[ot['name']]
            if isinstance(file_result, list):
                # File[] - read first file
                if len(file_result) > 0:
                    out_file = file_result[0]['location'].replace('file://', '')
                    out_content = _read_file_content(out_file)
            else:
                # Single File
                out_file = file_result['location'].replace('file://', '')
                out_content = _read_file_content(out_file)
        outs[ot['name']] = out_content
    return outs 