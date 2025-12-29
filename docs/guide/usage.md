# Usage with Coala Client

Coala Client is a simple command-line interface for LLM with MCP (Model Context Protocol) server support. It provides an easy way to interact with your MCP servers through natural language queries. Coala Client is a simple alternative to MCP-compatible clients such as Gemini CLI, Claude Code, Claude Desktop, ChatGPT Codex, Cursor, and other MCP-enabled applications.

## Installation

Install coala_client from GitHub using pip or uv:

```bash
# Using uv (recommended)
uv pip install git+https://github.com/hubentu/coala_client.git

# Or using pip
pip install git+https://github.com/hubentu/coala_client.git
```

## Configuration

### 1. Initialize Configuration

First, initialize the coala_client configuration:

```bash
coala init
```

This creates a default MCP servers configuration file at `~/.config/coala/mcp_servers.json`.

### 2. Configure MCP Servers

Edit `~/.config/coala/mcp_servers.json` to add your MCP servers. You can configure servers using the command-based approach, which automatically starts the server when needed:

```json
{
  "mcpServers": {
    "example": {
      "command": "python",
      "args": ["/path/to/example_server.py"],
      "env": {}
    },
    "vcf": {
      "command": "python",
      "args": ["/path/to/cmdagent/examples/vcf/vcf_question.py"],
      "env": {}
    }
  }
}
```

For example, to use the VCF analysis server from cmdagent:

```json
{
  "mcpServers": {
    "vcf": {
      "command": "python",
      "args": ["/home/qhu/Workspace/cmdagent/examples/vcf/vcf_question.py"],
      "env": {}
    }
  }
}
```

### 3. Set API Configuration

Configure your LLM provider. For example, with Ollama:

```bash
# Ollama doesn't require an API key (runs locally)
# Make sure Ollama is running: ollama serve
```

Or set environment variables for other providers:

```bash
# For OpenAI
export OPENAI_API_KEY=your-openai-api-key

# For Gemini
export GEMINI_API_KEY=your-gemini-api-key
```

## Basic Usage

### Interactive Chat

Start an interactive chat session:

```bash
# Use default provider (OpenAI)
coala

# Use a specific provider
coala -p ollama
coala -p gemini

# Use a specific model
coala -p ollama -m qwen3
```

When you start coala, it will automatically connect to all configured MCP servers:

```
Connecting to MCP server 'example'...
✓ Connected to 'example' (11 tools)
Connecting to MCP server 'vcf'...
✓ Connected to 'vcf' (3 tools)

╭───────────────────────────────────────────────────────────────────────────────────────────╮
│ Coala Client - LLM CLI with MCP Support                                                   │
│ Type '/help' for commands, '/exit' or Ctrl+C to quit                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────╯

Provider: ollama
Model: qwen3
Base URL: http://localhost:11434/v1

Connected servers (2):
  example: 11 tools
  vcf: 3 tools
```

### Example: Querying Gene Information

Once connected, you can ask natural language questions that will automatically use the available MCP tools:

```
You: summarize gene TP53 based on ncbi datasets
```

The LLM will:
1. Discover the available `ncbi_datasets_gene` tool from the vcf server
2. Understand that you want information about the TP53 gene
3. Invoke the tool with appropriate parameters
4. Present the results in a user-friendly format

**Example Response:**

> The **TP53** gene encodes a critical tumor suppressor protein (p53) that plays a central role in maintaining genomic stability and preventing cancer. Here's a summary of its key attributes and functions:
>
> ### **Core Information**
> - **Gene Symbol**: *TP53* (also known as *P53*, *BCC7*, *LFS1*, *BMFS5*, *TRP53*).
> - **Location**: Chromosome 17 (17p13.1) in humans.
> - **Function**: Regulates cell cycle arrest, apoptosis, DNA repair, senescence, and metabolic changes in response to cellular stress...
>
> ```
> Tool Invocation Summary:
> tool_name: ncbi_datasets_gene
> tool_version: staphb/ncbi-datasets
> ```

### Single Prompt Mode

You can also use coala for single queries without entering interactive mode:

```bash
coala ask "summarize gene TP53 based on ncbi datasets"
# or
coala -c "summarize gene TP53 based on ncbi datasets"
```

## Interactive Chat Commands

During an interactive chat session, you can use the following commands:

- `/help` - Show help message
- `/exit` or `/quit` - Exit the chat session
- `/clear` - Clear conversation history
- `/tools` - List all available MCP tools
- `/servers` - List connected MCP servers
- `/model` - Show current model information
- `/switch <provider>` - Switch to a different LLM provider

### Example: Listing Available Tools

```
You: /tools
```

This will display all available tools from all connected MCP servers, showing their names, descriptions, and parameters.

### Example: Checking Connected Servers

```
You: /servers
```

This will show:
```
Connected servers (2):
  example: 11 tools
  vcf: 3 tools
```

## Advanced Configuration

### Environment Variables

You can set environment variables for MCP servers by editing `~/.config/coala/env`:

```bash
# Environment variables for MCP servers
# Format: KEY=value

# Set default provider (openai, gemini, ollama, custom)
PROVIDER=ollama

# API keys and model settings
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3
```

## Complete Example Workflow

Here's a complete example of using coala_client with a VCF analysis server:

1. **Create the MCP server** (e.g., `examples/vcf/vcf_question.py`):
   ```python
   from coala.mcp_api import mcp_api
   import os
   base_dir = os.path.dirname(__file__)
   
   mcp = mcp_api(host='0.0.0.0', port=8000)
   mcp.add_tool(os.path.join(base_dir, 'ncbi_datasets_gene.cwl'), 'ncbi_datasets_gene', read_outs=True)
   mcp.add_tool(os.path.join(base_dir, 'bcftools_view.cwl'), 'bcftools_view', read_outs=False)
   mcp.add_tool(os.path.join(base_dir, 'biothings_query.cwl'), 'biothings_query', read_outs=True)
   mcp.serve()
   ```

2. **Configure coala_client** (`~/.config/coala/mcp_servers.json`):
   ```json
   {
     "mcpServers": {
       "vcf": {
         "command": "python",
         "args": ["/path/to/examples/vcf/vcf_question.py"],
         "env": {}
       }
     }
   }
   ```

3. **Start coala**:
   ```bash
   coala -p ollama -m qwen3
   ```

4. **Ask questions**:
   ```
   You: summarize gene TP53 based on ncbi datasets
   You: Subset variants in the gene TP53 from the ClinVar VCF file
   You: check the variant: 17 7673542 G A
   ```

## Benefits of Using Coala Client

- **Simple Interface**: Easy-to-use command-line interface for interacting with MCP servers
- **Multiple Providers**: Support for OpenAI, Gemini, Ollama, and custom OpenAI-compatible APIs
- **Automatic Tool Discovery**: Automatically discovers and uses available MCP tools
- **Interactive Chat**: Rich terminal UI with streaming responses
- **No Manual Tool Invocation**: The LLM automatically selects and invokes the appropriate tools based on your natural language queries

## Next Steps

- Learn more about [MCP Server setup](/guide/mcp-server)
- Explore [Function Call integration](/guide/function-call)
- Check out [use cases](/use-cases/) for more examples
