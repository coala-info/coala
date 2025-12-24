# Quick Start

Get up and running with Tool Agent in minutes.

## Basic Setup

The framework allows you to set up an MCP server with predefined tools for specific domains. For example, to create a bioinformatics-focused MCP server:

```python
from coala.mcp_api import mcp_api

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool('examples/ncbi_datasets_gene.cwl', 'ncbi_datasets_gene')
mcp.add_tool('examples/bcftools_view.cwl', 'bcftools_view', read_outs=False)
mcp.serve()
```

This creates an MCP server that exposes two bioinformatics tools:
- `ncbi_datasets_gene`: Retrieves gene metadata from NCBI datasets
- `bcftools_view`: Subsets and filters VCF/BCF files

## Start MCP Server

```bash
python examples/bioinfo_question.py
```

## Configure MCP Client

Once the server is running, you can configure your MCP client (e.g., in Cursor) to connect to it:

```json
{
    "mcpServers": {
        "coala": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable-http"
        }
    }
}
```

## Start Using

With this setup, you can ask the LLM natural language questions like:
- "Give me a summary about gene BRCA1"
- "Subset variants in the gene BRCA1 from the https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"

The LLM will automatically discover the available tools, understand their parameters, invoke the appropriate tool with the correct arguments, and present the results in a user-friendly format.

## Next Steps

- Learn more about [MCP Server setup](/guide/mcp-server)
- Explore [Function Call integration](/guide/function-call)
- Check out [use cases](/use-cases/)

