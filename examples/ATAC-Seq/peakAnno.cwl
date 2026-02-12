cwlVersion: v1.0
class: CommandLineTool
baseCommand: Rscript
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entryname: ChIPSeeker.R
    entry: "suppressPackageStartupMessages(library(R.utils))\nargs
      <- commandArgs(trailingOnly = TRUE, asValues = TRUE)\nChIPSeeker <-\nfunction(peak){\n
      \   library(ChIPseeker)\n    library(TxDb.Hsapiens.UCSC.hg38.knownGene)\n
      \ txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene \n
      \ fn <- basename(peak)\n    peakAnno <- annotatePeak(peak, TxDb = txdb)\n
      \   write.csv(data.frame(peakAnno), paste0(fn, \"_peakAnno.csv\"))\n    \n    pdf(paste0(fn,
      \"_AnnoPie.pdf\"))\n    plotAnnoPie(peakAnno)\n    dev.off()\n}\ndo.call(ChIPSeeker,
      args)"
    writable: false
- class: DockerRequirement
  dockerPull: hubentu/bioconductor-chipseeker:1.42.0
arguments:
- ChIPSeeker.R
id: ChIPSeeker
label: ChIP peak Annotation
doc: 'ChIPseeker: an R package for ChIP peak Annotation, Comparison and Visualization'
inputs:
  peak:
    label: peak
    doc: Bed format peak file, e.g. bed file or narrowPeak from macs
    type: File
    inputBinding:
      separate: true
outputs:
  ann:
    label: annotation
    doc: csv format peak annotatiion output
    type: File
    outputBinding:
      glob: '*peakAnno.csv'
  pie:
    label: pie
    doc: pie plot to show the percentages of gemomic features based on the peak annotation
    type: File
    outputBinding:
      glob: '*.pdf'
