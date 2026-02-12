cwlVersion: v1.0
class: CommandLineTool
baseCommand:
- macs3
- callpeak
requirements:
- class: DockerRequirement
  dockerPull: quay.io/biocontainers/macs3:3.0.3--py39h0699b22_0
label: macs3 callpeak
doc: the primary function in the MACS3 software suite used to find significantly
  enriched genomic regions (peaks) from ChIP-seq/ATAC-seq data, identifying protein binding sites or open chromatin by modeling background noise and improving spatial resolution of these regions.
inputs:
  treatment:
    label: treatment file
    doc: ATAC/ChIP-seq treatment file
    type: File
    inputBinding:
      prefix: -t
      separate: true
  control:
    label: control file
    doc: ATAC/ChIP-seq control file
    type: File?
    inputBinding:
      prefix: -c
      separate: true
  format:
    label: File format
    doc: format of input files. Choices are AUTO, BED, BAM, BAMPE, BEDPE, or FRAG. The default AUTO option will let MACS decide which format (except for BAMPE, BEDPE, and FRAG which should be explicitly set) the file is. Please note that if the format is set as BAMPE, BEDPE, or FRAG, MACS3 will call its special Paired-end mode to call peaks by piling up the actual ChIPed fragments defined by both aligned ends, instead of predicting the fragment size first and extending reads. The BEDPE only contains three columns. The FRAG format is for single-cell ATAC-seq fragment file which is a five columns BEDPE file with extra barcode and fragment count column. DEFAULT:AUTO
    type: string
    inputBinding:
      prefix: -f
      separate: true
  gsize:
    label: Effective genome size
    doc: |-
      It can be 1.0e+9 or 1000000000,
                              or shortcuts:'hs' for human (2.7e9), 'mm' for mouse
                              (1.87e9), 'ce' for C. elegans (9e7) and 'dm' for
                              fruitfly (1.2e8), Default:hs
    type: string?
    inputBinding:
      prefix: -g
      separate: true
  extsize:
    label: extension size
    doc: The arbitrary extension size in bp.
    type: int?
    inputBinding:
      prefix: --extsize
      separate: true
  shift:
    label: shift size
    doc: The arbitrary shift in bp.
    type: int?
    inputBinding:
      prefix: --shift
      separate: true
  keepdup:
    label: duplicate tags
    doc: It controls the MACS behavior towards duplicate tags at the exact same location.
      The 'auto' option makes MACS calculate the maximum tags at the exact same location
      based on binomal distribution using 1e-5 as pvalue cutoff. the 'all' option
      keeps every tags. The default 1 is to keep one tag at the same location.
    type: string?
    inputBinding:
      prefix: --keep-dup
      separate: true
  bdg:
    label: bedGraph
    doc: Whether or not to save extended fragment pileup and local lambda tracks at
      every bp into a bedGraph file.
    type: boolean?
    inputBinding:
      prefix: --bdg
      separate: true
  nomodel:
    label: shifting model
    doc: Whether or not to build the shifting model.
    type: boolean?
    inputBinding:
      prefix: --nomodel
      separate: true
  summits:
    label: summits
    doc: If set, MACS will use a more sophisticated signal processing approach to
      find subpeak summits in each enriched peak region.
    type: boolean?
    inputBinding:
      prefix: --call-summits
      separate: true
  qvalue:
    label: q-value cutoff
    doc: Minimum false discovery rate (FDR) threshold for peak calling. Peaks with q-value <= this threshold will be reported. Default is 0.05.
    type: float?
    inputBinding:
      prefix: --qvalue
      separate: true
  name:
    label: name
    doc: Experiment name, which will be used to generate outputfile names.
    type: string?
    inputBinding:
      prefix: -n
      separate: true
    default: test
outputs:
  narrowPeak:
    label: narrowPeak
    doc: BED6+4 format file which contains the peak locations together with peak summit,
      pvalue and qvalue
    type: File
    outputBinding:
      glob: '*.narrowPeak'
  xlsPeak:
    label: xlsPeak
    doc: a tabular file which contains information about called peaks. Additional
      information includes pileup and fold enrichment
    type: File
    outputBinding:
      glob: '*.xls'
  summitsBed:
    label: summits bed
    doc: peak summits locations for every peak. To find the motifs at the binding
      sites, this file is recommended.
    type: File?
    outputBinding:
      glob: '*summits.bed'
  controlBdg:
    label: controlBdg
    doc: bedGraph format for input control sample
    type: File?
    outputBinding:
      glob: '*lambda.bdg'
  teatBdg:
    label: teatBdg
    doc: bedGraph format for treatment sample
    type: File?
    outputBinding:
      glob: '*treat_pileup.bdg'
