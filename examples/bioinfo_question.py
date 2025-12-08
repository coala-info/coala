from cmdagent.mcp_api import mcp_api
import os
base_dir = os.path.dirname(__file__)

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool(os.path.join(base_dir, 'ncbi_datasets_gene.cwl'), 'ncbi_datasets_gene')
mcp.add_tool(os.path.join(base_dir, 'bcftools_view.cwl'), 'bcftools_view', read_outs=False)
mcp.serve()

# Question: give me a summary about gene "BRCA1"
# Question: Subset variants in the gene "BRCA1" from the https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz