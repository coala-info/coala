cwlVersion: v1.0
class: CommandLineTool
baseCommand: Rscript
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entryname: DEG.R
    entry: |-
      args <- commandArgs(trailingOnly = TRUE)
      DEG <-
      function(counts, group){
          library(DESeq2)
          cts <- read.csv(counts, row.names=1)
          group <- factor(gsub(" ", "", unlist(strsplit(group, split = ","))))
          coldata <- data.frame(group, row.names = colnames(cts))

          dds <- DESeqDataSetFromMatrix(countData = cts,
                                        colData = coldata,
                                        design= ~ group)
          dds <- DESeq(dds)
          deg <- results(dds)
          cont <- paste(rev(levels(group)), collapse="_")

          write.csv(deg, file = paste0("DEG_", cont, ".csv"))
      }
      DEG(args[1], args[2])
    writable: false
- class: DockerRequirement
  dockerPull: quay.io/biocontainers/bioconductor-deseq2:1.46.0--r44he5774e6_1
arguments:
- DEG.R
label: DEG
doc: Differentially Expressed Genes Analysis by DESeq2 package
inputs:
  counts:
    label: counts
    doc: Raw count matrix for RNASeq samples. Each row is a gene and each column is
      a sample.
    type: File
    inputBinding:
      position: 1
      separate: true
  group:
    label: group
    doc: Sample group labels separated by comma. Each sample has a group label, such
      as 'case,case,control,control'.
    type: string
    inputBinding:
      position: 2
      separate: true
outputs:
  deg:
    label: DEG output matrix
    doc: 'The DEG output matrix, containing the results columns: ''baseMean'', ''log2FoldChange'',
      ''lfcSE'', ''stat'', ''pvalue'' and ''padj'''
    type: File
    outputBinding:
      glob: '*csv'
