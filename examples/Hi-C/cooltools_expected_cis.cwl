cwlVersion: v1.2
class: CommandLineTool
label: cooltools expected-cis
doc: "Calculate expected Hi-C signal for cis regions (decay curve)."

requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: quay.io/biocontainers/cooltools:0.7.1--py311h93dcfea_3
  ResourceRequirement:
    # Links the nproc input to the actual reserved cores
    coresMin: $(inputs.nproc)

baseCommand: [cooltools, expected-cis]

inputs:
  cool_file:
    type: File
    doc: "The paths to a .cool or .mcool file."
    inputBinding:
      position: 1
      # Concatenates file path and URI: path/to/file.mcool::resolutions/1000
      valueFrom: $(self.path)::$(inputs.uri)

  uri:
    type: string
    doc: "The internal path/resolution within the mcool file."

  nproc:
    type: int
    default: 1
    doc: "Number of processes to split the work between."
    inputBinding:
      prefix: --nproc
      position: 2

  output_filename:
    type: string
    doc: "Output file name (e.g., expected.tsv)."
    inputBinding:
      prefix: -o
      position: 3

  view_bed:
    type: File?
    doc: "Path to a 3 or 4-column BED file with genomic regions."
    inputBinding:
      prefix: --view
      position: 4

  smooth:
    type: boolean?
    doc: "If set, cis-expected is smoothed."
    inputBinding:
      prefix: --smooth
      position: 5

  clr_weight_name:
    type: string?
    doc: "Use balancing weight with this name (default: weight)."
    inputBinding:
      prefix: --clr-weight-name
      position: 6

outputs:
  expected_tsv:
    type: File
    doc: "The calculated cis-expected signal in TSV format."
    outputBinding:
      glob: $(inputs.output_filename)