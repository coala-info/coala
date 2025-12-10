cwlVersion: v1.0
class: CommandLineTool
baseCommand: Rscript
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entryname: plotGSEA.R
    entry: |-
      suppressPackageStartupMessages(library(R.utils))
      args <- commandArgs(trailingOnly = TRUE, asValues = TRUE)
      plotGSEA <-
      function(pathway_plot, pathways, deg_res, rank_col = "stat"){
          library(fgsea)
          pathways <- readLines(pathways)
          path_list <- strsplit(pathways, split = " ")
          path_name <- lapply(path_list, function(x)x[1])
          path_list <- lapply(path_list, function(x)x[-1])
          names(path_list) <- unlist(path_name)

          deg <- read.csv(deg_res, row.names = 1)
          ranks <- deg[, rank_col]
          names(ranks) <- rownames(deg)
          ranks <- na.omit(ranks)

          p1 <- plotEnrichment(path_list[[pathway_plot]], ranks) + ggplot2::labs(title = pathway_plot)
          ggplot2::ggsave(p1, filename=paste0(pathway_plot, ".pdf"))
      }
      do.call(plotGSEA, args)
    writable: false
- class: DockerRequirement
  dockerPull: hubentu/gsea
arguments:
- plotGSEA.R
label: GSEA enrichment plot
doc: Create a enrichment plot for a pathway
inputs:
  pathway_plot:
    label: pathway_plot
    doc: The pathway ID to plot, which usually is the first column of GSEA outputs
    type: string
    inputBinding:
      position: 1
      separate: true
  pathways:
    label: pathways
    doc: The pathway file for gene sets
    type: File
    inputBinding:
      position: 2
      separate: true
  deg_res:
    label: DEG results
    doc: DEG results with gene symbols and statistical values
    type: File
    inputBinding:
      position: 3
      separate: true
  rank_col:
    label: rank column
    doc: The column of statistical results to rank the genes
    type: string
    inputBinding:
      position: 4
      separate: true
    default: stat
outputs:
  gsea_plot:
    label: gsea plot
    doc: A pdf file for the enrichment plot of a given pathway
    type: File
    outputBinding:
      glob: '*pdf'
