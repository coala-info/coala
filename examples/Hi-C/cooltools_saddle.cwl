cwlVersion: v1.2
class: CommandLineTool
label: cooltools saddle
doc: "Calculate saddle statistics and generate saddle plots."

requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: quay.io/biocontainers/cooltools:0.7.1--py311h93dcfea_3
  EnvVarRequirement:
    envDef:
      MPLBACKEND: Agg

baseCommand: [cooltools, saddle]

inputs:
  # --- Options ---
  qrange:
    type: float[]
    doc: "Low and high values used for quantile bins (e.g., [0.02, 0.98])."
    inputBinding:
      prefix: --qrange
      position: 1

  fig_format:
    type:
      - "null"
      - type: enum
        symbols: [png, jpg, svg, pdf]
    doc: "Generate a figure and save to a file of the specified format."
    inputBinding:
      prefix: --fig
      position: 2

  out_prefix:
    type: string
    doc: "Output prefix for the .npz and .tsv files."
    inputBinding:
      prefix: -o
      position: 3

  view:
    type: File?
    doc: "Path to a BED file containing genomic regions."
    inputBinding:
      prefix: --view
      position: 4

  # --- Positional Arguments ---
  cool_file:
    type: File
    doc: "Path to the cool file"
  uri:
    type: string
    doc: "Resolution path, e.g., resolutions/100000"
    inputBinding:
      position: 10
      valueFrom: $(inputs.cool_file.path)::$(self)

  track_file:
    type: File
  track_col:
    type: string
    doc: "Column name in the eigenvector file (usually E1)."
    inputBinding:
      position: 11
      valueFrom: $(inputs.track_file.path)::$(self)
    default: E1

  expected_file:
    type: File
  expected_col:
    type: string
    doc: "Column name in the expected file (usually balanced.avg)."
    inputBinding:
      position: 12
      valueFrom: $(inputs.expected_file.path)::$(self)
    default: balanced.avg

outputs:
  saddle_data:
    type: File
    doc: "Numpy .npz container with saddle data."
    outputBinding:
      glob: $(inputs.out_prefix).saddledump.npz

  saddle_tsv:
    type: File
    doc: "Digitized signal values in TSV format."
    outputBinding:
      glob: $(inputs.out_prefix).digitized.tsv

  saddle_plot:
    type: File?
    doc: "The generated saddle plot image."
    outputBinding:
      # Matches prefix + format (e.g., test_saddle.png)
      glob: $(inputs.out_prefix).$(inputs.fig_format)