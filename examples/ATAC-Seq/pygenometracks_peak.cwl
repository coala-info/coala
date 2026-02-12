cwlVersion: v1.2
class: CommandLineTool
baseCommand: pyGenomeTracks
arguments:
- --tracks
- peak.ini
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs.peak)
    entryname: peaks.narrowPeak
  - entry: $(inputs.bedgraph)
    entryname: treat_pileup.bdg
  - entry: $(inputs.gene)
    entryname: gene.bed
  - entryname: peak.ini
    entry: |-
      [bedgraph]
      file = treat_pileup.bdg
      title = Coverage
      height = 1.5
      file_type = bedgraph
      show_data_range = true
      [narrow_peak]
      file = peaks.narrowPeak
      title = Peaks from MACS3
      type = box
      height = 1.5
      line_width = 1.0
      file_type = narrow_peak
      show_labels = false
      [genes]
      file = gene.bed
      file_type = bed
      title = Gene
      height = 5.0
      [x-axis]
      where = bottom
- class: DockerRequirement
  dockerPull: quay.io/biocontainers/pygenometracks:3.9--pyhdfd78af_0
label: pyGenomeTracks
doc: Standalone program and library to plot beautiful genome browser tracks
inputs:
  peak:
    label: narrow peak
    doc: BED6+4 format file which contains the peaks from macs2 callpeak
    type: File
  bedgraph:
    label: bedgraph
    doc: bedGraph format for treatment sample
    type: File
  gene:
    label: gene
    doc: gene annotation file in bed format
    type: File
  region:
    label: region
    doc: Region to plot, the format is chr:start-end
    type: string
    inputBinding:
      prefix: --region
      separate: true
  outname:
    label: outname
    doc: File name to save the image
    type: string
    inputBinding:
      prefix: -o
      separate: true
outputs:
  trackplot:
    label: trackplot
    doc: output image of genomic tracks
    type: File
    outputBinding:
      glob: $(inputs.outname)
