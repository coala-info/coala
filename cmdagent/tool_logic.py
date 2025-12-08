# cmdagent/tool_logic.py
import os.path

def run_tool(tool, params, outputs, read_outs=True):
    # Prepare params for CWL tool
    inputs = tool.t.inputs_record_schema['fields']
    in_dict = {}
    for i in inputs:
        in_dict[i['name']] = i['type']

    for k, v in params.items():
        if k in in_dict:
            type_val = in_dict[k]
            # Handle both list and string types (e.g., ['null', 'File'] or 'File?')
            type_str = ' '.join(type_val) if isinstance(type_val, list) else str(type_val)
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
        type_val = ot['type']
        type_str = ' '.join(type_val) if isinstance(type_val, list) else str(type_val)
        if read_outs and 'File' in type_str:
            out_file = res[ot['name']]['location']
            with open(out_file.replace('file://', ''), 'r') as f:
                out_content = f.read().replace('\n', '')
        outs[ot['name']] = out_content
    return outs 