# coala/tool_logic.py
import os.path
import gzip

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

def run_tool(tool, params, outputs, read_outs=False):
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