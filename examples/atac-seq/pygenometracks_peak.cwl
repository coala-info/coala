cwlVersion: v1.0
class: CommandLineTool
baseCommand: pyGenomeTracks
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs.peak)
    entryname: peaks.narrowPeak
  - entry: $(inputs.bedgraph)
    entryname: treat_pileup.bdg
  - entry: $(inputs.gene)
    entryname: gene.bed
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
  tracks:
    label: tracks
    doc: The configure file is used to define the type of track. E.g. .bw for bigwig,
      .bed for bed etc
    type: File
    inputBinding:
      prefix: --tracks
      separate: true
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
