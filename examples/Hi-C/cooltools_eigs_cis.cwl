cwlVersion: v1.2
class: CommandLineTool
label: cooltools eigs-cis
doc: "Perform eigenvalue decomposition to calculate compartment signal."

requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: hubentu/cooltools_bedwig:0.7.1_2.10

baseCommand: [cooltools, eigs-cis]

inputs:
  bigwig:
    type: boolean?
    doc: "Also save compartment track (E1) as a bigWig file."
    inputBinding:
      prefix: --bigwig
      position: 1

  out_prefix:
    type: string
    doc: "Prefix for output files."
    inputBinding:
      prefix: -o
      position: 2

  view:
    type: File?
    doc: "Path to a BED file defining regions to use."
    inputBinding:
      prefix: --view
      position: 3

  phasing_track_file:
    type: File
    doc: "BedGraph-like file (e.g., GC content) to orient eigenvectors."
  
  phasing_track_col:
    type: string
    doc: "The column name in the phasing track file to use."
    inputBinding:
      prefix: --phasing-track
      position: 4
      # Concatenates: path/to/track.tsv::GC
      valueFrom: $(inputs.phasing_track_file.path)::$(self)

  n_eigs:
    type: int
    default: 1
    doc: "Number of eigenvectors to compute."
    inputBinding:
      prefix: --n-eigs
      position: 5

  cool_file:
    type: File
    doc: "The .cool or .mcool file."

  uri:
    type: string
    doc: "Internal path/resolution (e.g., resolutions/100000)."
    inputBinding:
      position: 6
      # Concatenates: path/to/file.mcool::resolutions/100000
      valueFrom: $(inputs.cool_file.path)::$(self)

outputs:
  eigenvectors:
    type: File
    doc: "TSV file containing eigenvectors."
    outputBinding:
      glob: $(inputs.out_prefix).cis.vecs.tsv

  lambdas:
    type: File
    doc: "Text file containing eigenvalues."
    outputBinding:
      glob: $(inputs.out_prefix).cis.lam.txt

  bigwig_out:
    type: File?
    doc: "BigWig file of the first eigenvector (if --bigwig was used)."
    outputBinding:
      glob: $(inputs.out_prefix).cis.bw
