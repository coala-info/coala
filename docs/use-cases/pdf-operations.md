# Use Case: PDF Page Extraction and Combination

## Overview

This use case demonstrates how to use the Tool Agent framework to perform PDF manipulation operations: extracting specific pages from a PDF file and combining multiple PDF files into one. These operations are commonly needed for document management, report generation, and file organization tasks.

## Setup

### MCP Server Configuration

Create an MCP server with PDF manipulation tools as shown in `examples/pdf_question.py`:

```python
from coala.mcp_api import mcp_api

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool('examples/pdftk_cat.cwl', 'pdftk_cat', read_outs=False)
mcp.serve()
```

This server exposes one tool:
- **`pdftk_cat`**: Extracts pages from PDF files or combines multiple PDF files using pdftk

### MCP Client Configuration

Configure your MCP client (e.g., in Cursor) to connect to the server:

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

## Use Case Workflow

### Step 1: Extract Specific Pages from a PDF

**User Query:**
```
extract page 2 and 3 from test_123.pdf to test_23.pdf
```

**What Happens:**
1. The LLM identifies that PDF page extraction is needed
2. It discovers the `pdftk_cat` tool via the MCP client
3. The tool is invoked with parameters:
   - `input_pdf1`: "examples/test_123.pdf" (source PDF file)
   - `page_ranges`: "2-3" (pages to extract)
   - `output_filename`: "test_23.pdf" (output filename)
4. The tool executes in a containerized environment, using pdftk to extract the specified pages
5. The extracted pages are saved as a new PDF file

**Results:**
- **Output file:** `test_23.pdf`
- **Size:** 1.8 KB
- **Content:** Pages 2 and 3 from the original `test_123.pdf` file
- **Location:** Workspace root directory

### Step 2: Combine Multiple PDF Files

**User Query:**
```
combine test_23.pdf and test_abc.pdf to test_23abc.pdf
```

**What Happens:**
1. The LLM identifies that PDF combination is needed
2. It discovers the `pdftk_cat` tool via the MCP client
3. The tool is invoked with parameters:
   - `input_pdf1`: "test_23.pdf" (first PDF file)
   - `input_pdf2`: "test_abc.pdf" (second PDF file)
   - `output_filename`: "test_23abc.pdf" (output filename)
4. The tool executes in a containerized environment, using pdftk to concatenate all pages from both PDFs
5. The combined PDF is saved as a new file

**Results:**
- **Output file:** `test_23abc.pdf`
- **Size:** 3.4 KB
- **Content:** All pages from `test_23.pdf` followed by all pages from `test_abc.pdf`
- **Location:** Workspace root directory


## Technical Details

### Tool Execution

The `pdftk_cat` tool executes in a Docker container as specified in its CWL definition:
- **Tool**: pdftk (PDF Toolkit)
- **Version**: pdftk/pdftk:latest
- **Operation**: Uses pdftk's `cat` command for page extraction and file combination

### Data Flow

1. For page extraction:
   - Input PDF is read from the specified path
   - Specified page range is extracted using pdftk
   - Output PDF is created with only the selected pages

2. For file combination:
   - Multiple input PDFs are read
   - All pages are concatenated in order
   - Output PDF contains all pages from all input files

### Output Files

The generated PDF files:
- Maintain original PDF formatting and quality
- Preserve page structure and content
- Are saved in the workspace directory for easy access

## Extending the Workflow

This use case can be extended to:
- Extract multiple non-contiguous page ranges (e.g., "1-5 10-15 20-end")
- Remove specific pages from a PDF
- Rotate or reorder pages
- Add watermarks or metadata
- Split large PDFs into smaller files
- Merge PDFs with custom page ordering

All of these extensions can be implemented by adding additional CWL tools to the MCP server and querying them through natural language.
