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

# Question: download sample information and count matrix for GSE164141
# Question: For the Count Matrix of GSE164141, sample can be labelled to 2 groups: minus,minus,minus,plus,plus,plus. Do a DEG for the samples between the two groups.
# Question: Download C4 pathways from msigdb.
# Question: Do a GSEA analysis using the previous DEG results and the downloaded C4 pathways.
# Question: create enrichment plot for "MORF_BUB3" pathway. 
