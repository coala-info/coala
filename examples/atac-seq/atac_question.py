from coala.mcp_api import mcp_api
import os
base_dir = os.path.dirname(__file__)

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool(os.path.join(base_dir, 'macs2_callpeak.cwl'), 'macs2_callpeak')
mcp.add_tool(os.path.join(base_dir, 'pygenometracks_peak.cwl'), 'pygenometracks_peak')
mcp.serve()

# ref: https://galaxyproject.github.io/training-material/topics/epigenetics/tutorials/atac-seq/tutorial.html
# Question: here is a treatment bed file for the ATAC-seq data: SRR891268_chr22.bed. Call peaks for the treatment bed file. According to the tutorial, the extension size should be 200bp and shift size should be -100.  Do not build the shifting model. keep all duplicate tags. save extended fragment pileup and local lambda tracks at every bp into a bedGraph file. use a more sophisticated signal processing approach to find subpeak summits in each enriched peak region.
# Question: We want to visulaize the narrow peaks in the chr22:37,193,000-37,252,000 region using pygenometracks. Use the chr22_gene.bed file as the gene annotation. The treatment bed graph from callpeak as the bedgraph coverage file. Use the peak.ini file as the configuration file.