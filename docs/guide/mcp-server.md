# MCP Server

The framework allows you to set up an MCP server with predefined tools for specific domains.

## Basic Example

For example, to create a bioinformatics-focused MCP server, you can use the following setup (as shown in [`examples/bioinfo_question.py`](https://github.com/rworkflow/coala/blob/master/examples/bioinfo_question.py)):

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

## MCP Client Configuration

You can configure your MCP client (e.g., in Cursor) to connect to the server in two ways:

### Option 1: Using Command Directly (Recommended)

The configuration can use a command directly, which will automatically start the server:

```json
{
    "mcpServers": {
        "pdf": {
            "command": "python",
            "args": ["/path/to/bioinfo_question.py"]
        }
    }
}
```

### Option 2: Using URL (Server Must Be Running)
Alternatively, starting the Server
```bash
python examples/bioinfo_question.py
```

If the server is already running, you can connect via URL:

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

## Usage Examples

With this setup, you can ask the LLM natural language questions like:
- "Give me a summary about gene BRCA1"
- "Subset variants in the gene BRCA1 from the https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"

The LLM will automatically discover the available tools, understand their parameters, invoke the appropriate tool with the correct arguments, and present the results in a user-friendly format.



## Demo

[![Demo md5](https://raw.githubusercontent.com/hubentu/coala/master/tests/coala.gif)](https://www.youtube.com/watch?v=QqevFmQbTDU)

