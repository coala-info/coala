# coala/tool_logic.py
import os
import os.path
import gzip
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import url2pathname
from cwltool.context import RuntimeContext


def _canonical_file_uri(uri: str) -> str:
    """Decode file:// to a local path, resolve it, return canonical file:// URI."""
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        raise ValueError("expected file URI")
    path_part = unquote(parsed.path or "")
    if os.name == "nt":
        local = url2pathname(path_part)
    else:
        local = path_part
    return Path(local).resolve().as_uri()


def _local_path_to_file_uri(path: str) -> str:
    """Build a file:// URI from a bare or relative local path (resolved)."""
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path(os.getcwd()) / p
    return p.resolve().as_uri()


def _remote_uri_string(s: str) -> bool:
    """True if s is a non-file URI (http(s), ftp, s3, …) — CWL string, not File."""
    if s.startswith(("http://", "https://", "ftp://")):
        return True
    return "://" in s and not s.startswith("file://")


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

    def path_to_file_obj(path_or_file):
        """Local paths and file:// become CWL File; remote URIs stay plain strings."""
        if path_or_file is None:
            return None
        if isinstance(path_or_file, dict):
            loc = path_or_file.get("location")
            if isinstance(loc, str):
                if _remote_uri_string(loc):
                    return loc
                if loc.startswith("file://"):
                    return {"class": "File", "location": _canonical_file_uri(loc)}
                return {"class": "File", "location": _local_path_to_file_uri(loc)}
            return path_or_file
        if isinstance(path_or_file, str):
            if _remote_uri_string(path_or_file):
                return path_or_file
            if path_or_file.startswith("file://"):
                return {"class": "File", "location": _canonical_file_uri(path_or_file)}
            return {"class": "File", "location": _local_path_to_file_uri(path_or_file)}
        return None

    def _is_file_array_type(typ):
        """True if typ is array of File (dict-like or in a union list)."""
        if hasattr(typ, 'get') and typ.get('type') == 'array':
            items = typ.get('items', '')
            return 'File' in str(items)
        if isinstance(typ, list):
            for t in typ:
                if t == 'null':
                    continue
                if hasattr(t, 'get') and t.get('type') == 'array':
                    if 'File' in str(t.get('items', '')):
                        return True
            return False
        return False

    def _is_single_file_type(typ):
        """True if typ is single File (not array)."""
        if hasattr(typ, 'get') and typ.get('type') == 'array':
            return False
        if isinstance(typ, list):
            for t in typ:
                if t != 'null' and hasattr(t, 'get') and t.get('type') == 'array':
                    return False
            return 'File' in ' '.join(str(t) for t in typ)
        return 'File' in str(typ) and '[]' not in str(typ)

    for k, v in params.items():
        if k not in in_dict or v is None:
            continue
        type_val = in_dict[k]
        type_str = ' '.join(str(t) for t in type_val) if isinstance(type_val, list) else str(type_val)
        if 'File' not in type_str:
            continue
        is_file_array = _is_file_array_type(type_val)
        if is_file_array and isinstance(v, list):
            # CWL expects list of File; normalize list of path strings to list of File objects
            converted = [path_to_file_obj(item) for item in v]
            if all(x is not None for x in converted):
                params[k] = converted
        elif _is_single_file_type(type_val):
            # Single File: accept one path/dict or a list of one
            to_convert = v[0] if isinstance(v, list) and len(v) > 0 else v
            file_obj = path_to_file_obj(to_convert)
            if file_obj is not None:
                params[k] = file_obj
    
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