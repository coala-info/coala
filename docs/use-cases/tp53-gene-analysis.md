# Use Case: TP53 Gene Analysis with ClinVar Variants

## Overview

This use case demonstrates how to use Coala to perform a complete gene analysis workflow: first retrieving gene metadata from NCBI, then subsetting relevant variants from a large VCF file. We'll use the TP53 gene as an example, which is a critical tumor suppressor gene associated with many human cancers.

## Setup

### MCP Server Configuration

Create an MCP server with bioinformatics tools as shown in `examples/vcf_question.py`:

```python
from coala.mcp_api import mcp_api

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool('examples/ncbi_datasets_gene.cwl', 'ncbi_datasets_gene')
mcp.add_tool('examples/bcftools_view.cwl', 'bcftools_view', read_outs=False)
mcp.add_tool('examples/biothings_query.cwl', 'biothings_query')
mcp.serve()
```

This server exposes three tools:
- **`ncbi_datasets_gene`**: Retrieves comprehensive gene metadata from [NCBI Datasets](#ncbi-datasets)
- **`bcftools_view`**: Subsets and filters VCF/BCF files by genomic regions
- **`biothings_query`**: Queries biological databases (genes, variants, chemicals, diseases) via [BioThings](#biothings) APIs

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

### Step 1: Retrieve Gene Information

**User Query:**
```
give me a summary about gene "TP53"
```

**Tool Invocation:**
```json
{
  "tool": "ncbi_datasets_gene",
  "parameters": {
    "gene": "TP53",
    "taxon": "human"
  }
}
```

**Tool Response:**
```json
{
  "gene_info": {
    "gene_id": "7157",
    "symbol": "TP53",
    "description": "tumor protein p53",
    "chromosome": "17",
    "genomic_range": {
      "begin": 7668421,
      "end": 7687490
    }
  },
  "tool_name": "ncbi_datasets_gene",
  "tool_version": "ncbi/datasets-cli:latest"
}
```

**Chat Response:**
> Here's a summary of the **TP53** gene:
>
> **Basic Information:**
> - **Gene Name:** TP53 (tumor protein p53)
> - **Gene ID:** 7157
> - **Chromosome:** 17
> - **Location (GRCh38.p14):** Chromosome 17: 7,668,421-7,687,490
>
> **Function:**
> TP53 is a tumor suppressor protein with transcriptional activation, DNA binding, and oligomerization domains. It plays critical roles in:
> - DNA damage response
> - Cell cycle regulation
> - Apoptosis
> - Cellular senescence
>
> **Clinical Significance:**
> Mutations in TP53 are associated with many human cancers, including Li-Fraumeni syndrome.
>
> **Transcripts:** 26 total (25 protein-coding, 1 non-coding)

### Step 2: Subset Variants from ClinVar VCF

**User Query:**
```
Subset variants in the gene "TP53" from the https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
```

**Tool Invocation:**
```json
{
  "tool": "bcftools_view",
  "parameters": {
    "vcf": "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz",
    "region": "17:7668421-7687490",
    "fout": "tp53_variants.vcf.gz",
    "otype": "z"
  }
}
```

**Tool Response:**
```json
{
  "vcf_out": {
    "basename": "tp53_variants.vcf.gz",
    "size": 281600
  },
  "tool_name": "bcftools_view",
  "tool_version": "quay.io/biocontainers/bcftools:1.13--h3a49de5_0"
}
```

**Chat Response:**
> Successfully extracted TP53 variants from the ClinVar VCF file.
>
> **Output Details:**
> - **File:** `tp53_variants.vcf.gz`
> - **Size:** ~275 KB (compressed)
> - **Format:** Compressed VCF (gzipped)
>
> **Extraction Parameters:**
> - **Source:** ClinVar VCF (GRCh38)
> - **Region:** Chromosome 17: 7,668,421-7,687,490 (TP53 gene coordinates)
>
> **Content:**
> The output file contains all ClinVar variants overlapping the TP53 gene region. These variants include pathogenic, likely pathogenic, benign, likely benign, and variants of uncertain significance associated with TP53.
>
> You can further filter these variants by clinical significance or perform additional analysis on the extracted subset.

### Step 3: Query Variant Information

**User Query:**
```
check the variant: 17 7673542 G A
```

**Tool Invocation:**
```json
{
  "tool": "biothings_query",
  "parameters": {
    "client": "variant",
    "get": "chr17:g.7673542G>A",
    "fields": "all",
    "assembly": "hg38",
    "pretty": true
  }
}
```

**Chat Response:**

> **Variant Report: chr17:7673542 G>A**
>
> | Property | Value |
> |----------|-------|
> | **Variant ID** | chr17:g.7673542G>A |
> | **rsID** | rs969930693 |
> | **Gene** | TP53 |
> | **Cytogenetic Location** | 17p13.1 |
> | **Variant Type** | Single Nucleotide Variant (SNV) |
>
> **HGVS Nomenclature:**
> - Genomic: NC_000017.11:g.7673542G>A
> - Coding (canonical): NM_000546.6:c.986C>T
> - Protein: p.Thr329Ile (T329I)
>
> **Protein Domain:** Located in the p53 tetramerization domain
>
> **ClinVar Clinical Significance:**
> | Condition | Significance |
> |-----------|--------------|
> | Li-Fraumeni syndrome (LFS) | Uncertain significance |
> | Hereditary cancer-predisposing syndrome | Conflicting interpretations |
>
> **Population Frequency (gnomAD Exomes):**
> - Global: 3.98 × 10⁻⁶ (1 allele / 251,390)
> - Extremely rare variant
>
> **Pathogenicity Predictions:**
> | Tool | Prediction | Score |
> |------|------------|-------|
> | AlphaMissense | Benign | 0.165 |
> | REVEL | - | 0.758 |
> | CADD | - | 22.5 (Phred) |
> | MetaSVM | Damaging | 1.15 |
> | MutationTaster | Disease-causing | 0.91 |
>
> **Summary:** This is a rare missense variant (p.Thr329Ile) in the TP53 tetramerization domain. Clinical significance is currently classified as uncertain or conflicting, primarily associated with Li-Fraumeni syndrome. Computational predictions are mixed.

## Key Benefits

1. **Natural Language Interface**: Complex bioinformatics workflows are accessible through simple queries
2. **Automatic Tool Discovery**: The LLM automatically selects the appropriate tools based on the task
3. **Parameter Extraction**: Genomic coordinates are automatically extracted from gene metadata for downstream analysis
4. **Containerized Execution**: Tools run in isolated containers, ensuring reproducibility and avoiding dependency conflicts
5. **Seamless Integration**: Multiple tools work together in a single workflow without manual intervention
6. **Remote Data Access**: Direct access to remote VCF files without manual download
7. **Human-in-the-Loop Analysis**: Users maintain full control throughout the analysis process. You can specify different genes, adjust genomic regions, filter variants by clinical significance, change output formats, and query different VCF sources—all through natural language interaction without modifying code

## Technical Details

### Tool Execution

All tools execute in Docker containers as specified in their CWL definitions:
- **[NCBI Datasets](#ncbi-datasets)**: Queries NCBI's gene database API
- **[BCFtools](#bcftools)**: Uses bcftools 1.13 for VCF processing
- **[BioThings](#biothings)**: Queries BioThings APIs for variant annotations, including ClinVar, gnomAD, and pathogenicity predictions

### Data Flow

1. Gene metadata is retrieved as JSON from NCBI
2. Genomic coordinates are parsed from the metadata
3. These coordinates are used to subset the VCF file
4. The subsetted VCF is saved as a compressed file
5. Individual variants can be queried for detailed annotations including clinical significance, population frequencies, and pathogenicity predictions

### Output Files

The subsetted VCF file contains:
- All variants from ClinVar that overlap the TP53 gene region
- Standard VCF format with headers and variant records
- Compressed format for efficient storage

## Extending the Workflow

This use case can be extended to:
- Filter variants by clinical significance
- Annotate variants with additional databases
- Perform statistical analysis on variant frequencies
- Generate visualizations of variant distribution
- Compare variants across different populations

All of these extensions can be implemented by adding additional CWL tools to the MCP server and querying them through natural language.

## Reference

<a id="bcftools"></a>
BCFtools
https://github.com/samtools/bcftools

<a id="ncbi-datasets"></a>
NCBI Datasets (ncbi_datasets_gene)
https://github.com/ncbi/datasets

<a id="biothings"></a>
BioThings
https://biothings.io/

