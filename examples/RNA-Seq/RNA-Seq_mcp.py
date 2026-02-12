from coala.mcp_api import mcp_api
import os
base_dir = os.path.dirname(__file__)

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool(os.path.join(base_dir, 'getGEOs.cwl'), 'getGEOs')
mcp.add_tool(os.path.join(base_dir, 'DEG.cwl'), 'DEG')
mcp.add_tool(os.path.join(base_dir, 'pathdb.cwl'), 'pathdb')
mcp.add_tool(os.path.join(base_dir, 'gsea.cwl'), 'gsea')
mcp.add_tool(os.path.join(base_dir, 'plotGSEA.cwl'), 'plotGSEA')
mcp.serve()

