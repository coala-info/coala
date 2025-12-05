# cmdagent/tool_logic.py

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
                    v = v['location']
                params[k] = {
                    "class": "File",
                    "location": v
                }
    res = tool(**params)
    outs = {}
    for ot in outputs:
        out_content = res[ot['name']]
        if read_outs and 'File' in ot['type']:
            out_file = res[ot['name']]['location']
            with open(out_file.replace('file://', ''), 'r') as f:
                out_content = f.read().replace('\n', '')
        outs[ot['name']] = out_content
    return outs 