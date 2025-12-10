cwlVersion: v1.2
class: CommandLineTool
baseCommand: Rscript
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entryname: gsea.R
    entry: "suppressPackageStartupMessages(library(R.utils))\nargs <- commandArgs(trailingOnly
      = TRUE, asValues = TRUE)\nargs[[\"pvalue\"]] <- as.numeric(args[[\"pvalue\"]])\ngsea
      <-\nfunction(deg_res, pathways, rank_col = \"stat\", pvalue = 0.01) {\n    library(fgsea)\n
      \   deg <- read.csv(deg_res, row.names = 1)\n\n    pathways <- readLines(pathways)\n
      \   path_list <- strsplit(pathways, split = \" \")\n    path_name <- lapply(path_list,
      function(x)x[1])\n    path_list <- lapply(path_list, function(x)x[-1])\n    names(path_list)
      <- unlist(path_name)\n    \n    ranks <- deg[, rank_col]\n    names(ranks) <-
      rownames(deg)\n    ranks <- na.omit(ranks)\n    \n    gsea_res <- fgsea(pathways
      = path_list, stats = ranks)\n    gsea_res <- gsea_res[gsea_res$padj < as.numeric(pvalue),
      ]\n    gsea_res <- data.frame(gsea_res[order(pval), ])\n    gsea_res <- apply(gsea_res,
      2, as.character)\n    write.csv(gsea_res, file=\"gsea_ranked.csv\")\n}\ndo.call(gsea,
      args)"
    writable: false
- class: DockerRequirement
  dockerPull: hubentu/gsea
- class: NetworkAccess
  networkAccess: true
arguments:
- gsea.R
label: gene set enrichment analysis (GSEA)
doc: Run GSEA to determine whether an a priori defined set of genes shows statistically
  significant, concordant differences between two biological states
inputs:
  deg_res:
    label: deg_res
    doc: DEG results containing gene symbols and statistical results
    type: File
    inputBinding:
      prefix: deg_res=
      separate: false
  pathways:
    label: pathways
    doc: pathway file containing multiple gene sets
    type: File
    inputBinding:
      prefix: pathways=
      separate: false
  rank_col:
    label: rank column
    doc: The colume name including statistical values for ranking
    type: string
    inputBinding:
      prefix: rank_col=
      separate: false
    default: stat
  pvalue:
    label: p value
    doc: adjusted p value cutoff for significant pathways
    type: float
    inputBinding:
      prefix: pvalue=
      separate: false
    default: 0.01
outputs:
  gsea:
    label: gsea
    doc: GSEA analysis results including significant pathways and statistical values
    type: File
    outputBinding:
      glob: '*csv'
