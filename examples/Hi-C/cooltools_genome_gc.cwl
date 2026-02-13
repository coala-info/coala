cwlVersion: v1.2
class: CommandLineTool
label: cooltools genome gc
doc: "Calculate GC content for genomic bins using a reference FASTA."

requirements:
  DockerRequirement:
    # Use the image we built in the previous step
    dockerPull: quay.io/biocontainers/cooltools:0.7.1--py311h93dcfea_3

baseCommand: [cooltools, genome, gc]

inputs:
  bins_file:
    type: File
    doc: "TSV file containing genomic bins (e.g., from cooler dump)."
    inputBinding:
      position: 1

  genome_fasta:
    type: File
    doc: "Reference genome FASTA file."
    secondaryFiles:
      - .fai
    inputBinding:
      position: 2

  output_filename:
    type: string
    default: "gc_content.tsv"

# Captures the standard output stream (>) into a file
stdout: $(inputs.output_filename)

outputs:
  gc_tsv:
    type: stdout
    doc: "TSV file with an additional 'GC' column."