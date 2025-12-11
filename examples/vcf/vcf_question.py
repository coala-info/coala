from coala.mcp_api import mcp_api
import os
base_dir = os.path.dirname(__file__)

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool(os.path.join(base_dir, 'ncbi_datasets_gene.cwl'), 'ncbi_datasets_gene', read_outs=True)
mcp.add_tool(os.path.join(base_dir, 'bcftools_view.cwl'), 'bcftools_view', read_outs=False)
mcp.add_tool(os.path.join(base_dir, 'biothings_query.cwl'), 'biothings_query', read_outs=True)
mcp.serve()

# Question: give me a summary about gene "TP53". get the gene genomic position.
# Question: Subset variants in the gene "TP53" to a vcf file from the https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.
# Question: check the variant: 17 7673542 G A