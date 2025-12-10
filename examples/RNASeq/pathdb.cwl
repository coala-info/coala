cwlVersion: v1.0
class: CommandLineTool
baseCommand: Rscript
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entryname: pathdb.R
    entry: |-
      suppressPackageStartupMessages(library(R.utils))
      args <- commandArgs(trailingOnly = TRUE, asValues = TRUE)
      pathdb <-
      function(species = "human", pathway_collection = "H"){
          library(msigdbr)
          pathways <- msigdbr(species = species,
                              collection = pathway_collection)
          pathways <- split(as.character(pathways$gene_symbol), pathways$gs_name)
          path_list <- lapply(names(pathways), function(x)paste(c(x, pathways[[x]]), collapse=" "))
          writeLines(unlist(path_list), gsub(" ", "", paste0(species, "_", pathway_collection, "_pathway.txt")))
      }
      do.call(pathdb, args)
    writable: false
- class: DockerRequirement
  dockerPull: hubentu/gsea
arguments:
- pathdb.R
label: msigdb pathway database
doc: Download pathways from msigdb database
inputs:
  species:
    label: species
    doc: Species name for output genes, such as 'Homo sapiens' or 'Mus musculus'.
      Both scientific and common names are acceptable
    type: string
    inputBinding:
      position: 1
      separate: true
  collection:
    label: collection
    doc: Collection abbreviation, such as 'H' or 'C1'
    type: string
    inputBinding:
      position: 2
      separate: true
outputs:
  pathway:
    label: pathway
    doc: Downloaded pathways. Each row is a pathway. First item is the pathway ID
      and thre rests are gene symbols.
    type: File
    outputBinding:
      glob: '*txt'
