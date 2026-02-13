cwlVersion: v1.2
class: CommandLineTool
label: cooler dump
doc: "Dump a cooler's data (bins, pixels, or chroms) to a text file."

requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: quay.io/biocontainers/cooltools:0.7.1--py311h93dcfea_3

baseCommand: [cooler, dump]

inputs:
  header:
    type: boolean
    default: true
    doc: "Print the header of column names as the first row."
    inputBinding:
      prefix: --header
      position: 1

  table:
    type:
      - "null"
      - type: enum
        symbols: [chroms, bins, pixels]
    default: bins
    doc: "Which table to dump."
    inputBinding:
      prefix: --table
      position: 2

  cool_file:
    type: File
    doc: "Path to the .cool or .mcool file."
    inputBinding:
      # The positional argument COOL_PATH usually comes after options
      position: 10
      valueFrom: $(self.path)::$(inputs.uri)

  uri:
    type: string
    doc: "The internal path/resolution (e.g., resolutions/1000)."

  output_filename:
    type: string
    doc: "The name of the output text file (e.g., bins.tsv)."
    inputBinding:
      prefix: --out
      position: 11

  # Optional helper for large pixel dumps
  join:
    type: boolean?
    doc: "Print full chromosome bin coordinates instead of bin IDs."
    inputBinding:
      prefix: --join
      position: 3

outputs:
  dump_output:
    type: File
    doc: "The dumped text file."
    outputBinding:
      glob: $(inputs.output_filename)