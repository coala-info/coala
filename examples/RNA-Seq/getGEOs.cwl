cwlVersion: v1.0
class: CommandLineTool
baseCommand: Rscript
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entryname: getGEOs.R
    entry: "suppressPackageStartupMessages(library(R.utils))\nargs <- commandArgs(trailingOnly
      = TRUE, asValues = TRUE)\ngetGEOs <-\nfunction(geo){\n    library(GEOquery)\n
      \   series <- getGEO(geo, destdir = \"./\")\n    sf <- normalizePath(file.path(\"./\",
      names(series)))\n    lapply(sf, function(x)file.copy(x, basename(x)))\n    \n
      \   sup <- rownames(getGEOSuppFiles(geo))\n    lapply(sup, function(x)file.copy(x,
      basename(x)))\n    ## file.copy(sup, basename(sup))\n    ## return(basename(sup))\n}\ndo.call(getGEOs,
      args)"
    writable: false
- class: DockerRequirement
  dockerPull: quay.io/biocontainers/bioconductor-geoquery:2.74.0--r44hdfd78af_0
arguments:
- getGEOs.R
label: getGEO
doc: Given a GEO ID, download meta (sample and platform) information and downloads
  processeed expression Matrix file from GEO database.
inputs:
  geo:
    label: GEO dataset ID
    doc: GSE, GEO dataset ID, such as GSE164141
    type: string
    inputBinding:
      prefix: geo=
      separate: false
outputs:
  mfile:
    label: GSE series matrix
    doc: ' pre-processed, tab-delimited text file with sample and gene metadata, essential
      for bioinformatics analysis to find differentially expressed genes.'
    type: File[]
    outputBinding:
      glob: '*txt.gz'
  sfile:
    label: GSE Supplementary file
    doc: supplementary dataset or raw data. count matrices for RNASeq data
    type: File[]
    outputBinding:
      glob: '*csv.gz'
