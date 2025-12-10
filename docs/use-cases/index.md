# Use Cases

This section contains real-world examples and use cases demonstrating how to use Tool Agent in various scenarios.

## Available Use Cases

### [TP53 Gene Analysis with ClinVar Variants](./tp53-gene-analysis)

This use case demonstrates how to use the Tool Agent framework to perform a complete gene analysis workflow: first retrieving gene metadata from NCBI, then subsetting relevant variants from a large VCF file. We'll use the TP53 gene as an example, which is a critical tumor suppressor gene associated with many human cancers.

### [PDF Page Extraction and Combination](./pdf-operations)

This use case demonstrates how to use the Tool Agent framework to perform PDF manipulation operations: extracting specific pages from a PDF file and combining multiple PDF files into one. These operations are commonly needed for document management, report generation, and file organization tasks.

### [RNA-Seq Differential Expression and Pathway Analysis](./rnaseq-analysis)

This use case demonstrates how to use the Tool Agent framework to perform a complete RNA-Seq analysis workflow: downloading data from GEO, performing differential gene expression (DEG) analysis using DESeq2, running Gene Set Enrichment Analysis (GSEA), and generating enrichment plots. The workflow showcases how multiple bioinformatics tools can be chained together through natural language queries.

## Key Benefits

- **Natural Language Interface**: Complex bioinformatics workflows are accessible through simple queries
- **Automatic Tool Discovery**: The LLM automatically selects the appropriate tools based on the task
- **Parameter Extraction**: Genomic coordinates are automatically extracted from gene metadata for downstream analysis
- **Containerized Execution**: Tools run in isolated containers, ensuring reproducibility and avoiding dependency conflicts
- **Seamless Integration**: Multiple tools work together in a single workflow without manual intervention
- **Remote Data Access**: Direct access to remote VCF files without manual download

