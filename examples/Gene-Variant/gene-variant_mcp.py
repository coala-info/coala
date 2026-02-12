from coala.mcp_api import mcp_api
import os
base_dir = os.path.dirname(__file__)

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool(os.path.join(base_dir, 'ncbi_datasets_gene.cwl'), 'ncbi_datasets_gene', read_outs=True)
mcp.add_tool(os.path.join(base_dir, 'bcftools_view.cwl'), 'bcftools_view', read_outs=False)
mcp.add_tool(os.path.join(base_dir, 'biothings_query.cwl'), 'biothings_query', read_outs=True)
mcp.serve()

