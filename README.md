# Coala README
======================

## Overview

Coala (local COmmAnd-line LLM-agent Adapter) is a Python package that converts any command-line tool into a Large Language Model (LLM) agent. This allows you to interact with the tool using natural language, making it easier to use and integrate with other applications.

## Requirements

* Python 3.12 or later
* FastAPI
* Requests
* Pydantic
* Uvicorn
* cwltool
* mcp (Model Context Protocol SDK)

## Installation

To install Coala, run the following command:
```bash
pip install git+https://github.com/hubentu/coala
```

## How the Framework Works

Coala leverages the Model Context Protocol (MCP) to bridge command-line tools and Large Language Models (LLMs). The framework works by converting CWL (Common Workflow Language) tool definitions into MCP-compatible agents that can be discovered and invoked by LLMs through natural language queries. Here's how it works: you create an MCP server instance using `mcp_api`, register your domain-specific tools by providing their CWL definitions via `add_tool()`, and then start the server. The MCP server exposes these tools as discoverable agents that any MCP-compatible client (like Cursor) can query and invoke. When an LLM needs to use a tool, it queries the MCP server for available tools, selects the appropriate one, and invokes it with the necessary parameters. The tool executes within a containerized environment (as specified in the CWL), processes the request, and returns results back through the MCP protocol to the LLM, which then presents the answer to the user in natural language.

## Usage

### MCP server

The framework allows you to set up an MCP server with predefined tools for specific domains. For example, to create a bioinformatics-focused MCP server, you can use the following setup (as shown in [`examples/bioinfo_question.py`](examples/bioinfo_question.py)):

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

With this setup, you can ask the LLM natural language questions like:
- "Give me a summary about gene BRCA1"
- "Subset variants in the gene BRCA1 from the https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"

The LLM will automatically discover the available tools, understand their parameters, invoke the appropriate tool with the correct arguments, and present the results in a user-friendly format.

* Start MCP server
```
python examples/bioinfo_question.py
```

* Call by MCP client from Cursor
[![Demo md5](tests/coala.gif)](https://www.youtube.com/watch?v=QqevFmQbTDU)


### Function call
* Creating an API

To create an API, import the `tool_api` function from `coala.remote_api` and pass in the path to a CWL file and the name of the tool:
```python
from coala.remote_api import tool_api

api = tool_api(cwl_file='tests/dockstore-tool-md5sum.cwl', tool_name='md5sum')
api.serve()
```
The `api.serve()` method will start a RESTful API as a service, allowing you to run the tool remotely from the cloud or locally.

* Creating a Tool Agent

To create a tool agent, import the `tool_agent` function from `coala.agent` and pass in the API instance:
```python
from coala.agent import tool_agent

ta = tool_agent(api)
md5 = ta.create_tool()
md5(input_file="tests/dockstore-tool-md5sum.cwl")
```
Function `md5` is created automatically based on the `api`.

* Function call with Gemini

To integrate the tool agent with Gemini, import the `GenerativeModel` class from `google.generativeai` and create a new instance:
```python
import google.generativeai as genai

genai.configure(api_key="******")
model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=[md5])

chat = model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message("what is md5 of tests/dockstore-tool-md5sum.cwl?")
response.text
```
```
'The md5sum of tests/dockstore-tool-md5sum.cwl is ad59d9e9ed6344f5c20ee7e0143c6c12. \n'
```
