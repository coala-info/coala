cwlVersion: v1.2
class: CommandLineTool
baseCommand: []
requirements:
- class: DockerRequirement
  dockerPull: hubentu/biothings:0.4.1
- class: NetworkAccess
  networkAccess: true
label: biothings_query
doc: BioThings API Client - Query biological databases via BioThings APIs.
inputs:
  client:
    label: client
    doc: "Client type to use. Options: gene, variant, chem, disease, geneset, taxon."
    type: string?
    inputBinding:
      prefix: --client
      separate: true
  get:
    label: get
    doc: "Get a single item by ID. Example: 1017 (gene), chr7:g.140453134T>C (variant)"
    type: string?
    inputBinding:
      prefix: --get
      separate: true
  query:
    label: query
    doc: "Search/query for items matching a term. Example: cdk2, symbol:BRCA1"
    type: string?
    inputBinding:
      prefix: --query
      separate: true
  batch:
    label: batch
    doc: "Get multiple items by comma-separated IDs. Example: 1017,1018,1019"
    type: string?
    inputBinding:
      prefix: --batch
      separate: true
  fields:
    label: fields
    doc: "Comma-separated list of fields to return. Use all for all fields."
    type: string?
    inputBinding:
      prefix: --fields
      separate: true
  size:
    label: size
    doc: "Number of results to return for queries (default: 10, max: 1000)"
    type: int?
    inputBinding:
      prefix: --size
      separate: true
  assembly:
    label: assembly
    doc: "Genome assembly for variant queries: hg19 (default) or hg38."
    type: string?
    inputBinding:
      prefix: --assembly
      separate: true
  pretty:
    label: pretty
    doc: Pretty print JSON output with indentation
    type: boolean?
    inputBinding:
      prefix: --pretty
      separate: true
  output:
    label: output
    doc: Output file name for results (JSON format)
    type: string
    inputBinding:
      prefix: --output
      separate: true
    default: result.json
outputs:
  result:
    label: result
    doc: JSON file containing query results from BioThings API
    type: File
    outputBinding:
      glob: "*.json"
