cwlVersion: v1.2
class: CommandLineTool
label: cooltools insulation
doc: "Calculate diamond insulation scores and call insulating boundaries."

requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    # Use the image containing cooltools and ucsc-bedgraphtobigwig
    dockerPull: hubentu/cooltools_bedwig:0.7.1_2.10

baseCommand: [cooltools, insulation]

inputs:
  # --- Positional Arguments ---
  cool_file:
    type: File
    doc: "Path to a .cool or .mcool file."

  uri:
    type: string
    doc: "Internal path/resolution (e.g., resolutions/10000)."
    inputBinding:
      position: 10
      valueFrom: $(inputs.cool_file.path)::$(self)

  window:
    type: int[]
    doc: "Window size(s) for insulation calculation in bp (or pixels if --window-pixels is set)."
    inputBinding:
      position: 11

  # --- Options ---
  nproc:
    type: int?
    default: 1
    inputBinding:
      prefix: --nproc
  
  output_filename:
    type: string
    doc: "The output TSV file"
    inputBinding:
      prefix: --output

  view:
    type: File?
    inputBinding:
      prefix: --view

  threshold:
    type: string?
    default: "Li"
    doc: "Thresholding rule (Li, Otsu, or a float)."
    inputBinding:
      prefix: --threshold

  bigwig:
    type: boolean?
    inputBinding:
      prefix: --bigwig

  window_pixels:
    type: boolean?
    inputBinding:
      prefix: --window-pixels

outputs:
  insulation_tsv:
    type: File
    outputBinding:
      glob: $(inputs.output_filename)

  insulation_bigwigs:
    type: File[]?
    outputBinding:
      # Matches output.<window>.bw as per help docs
      glob: "*.bw"