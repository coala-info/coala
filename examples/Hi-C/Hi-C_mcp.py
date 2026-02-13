from coala.mcp_api import mcp_api
import os
base_dir = os.path.dirname(__file__)

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool(os.path.join(base_dir, 'cooler_dump.cwl'))
mcp.add_tool(os.path.join(base_dir, 'cooler_show.cwl'))
mcp.add_tool(os.path.join(base_dir, 'cooltools_eigs_cis.cwl'))
mcp.add_tool(os.path.join(base_dir, 'cooltools_expected_cis.cwl'))
mcp.add_tool(os.path.join(base_dir, 'cooltools_genome_gc.cwl'))
mcp.add_tool(os.path.join(base_dir, 'cooltools_insulation.cwl'))
mcp.add_tool(os.path.join(base_dir, 'cooltools_saddle.cwl'))
mcp.serve()
