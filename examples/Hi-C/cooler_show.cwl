cwlVersion: v1.0
class: CommandLineTool
baseCommand:
- cooler
- show
requirements:
- class: DockerRequirement
  dockerPull: quay.io/biocontainers/cooltools:0.7.1--py311h93dcfea_3
- class: InlineJavascriptRequirement
id: cooler_show
doc: Display and browse a cooler in matplotlib.
inputs:
  fcool:
    doc: Path to a COOL file or Cooler URI
    type: File
    inputBinding:
      position: 1
      separate: true
      valueFrom: $(self.path)::$(inputs.uri)
  uri:
    doc: 'Coolers URI, example: resolutions/100000'
    type: string
  range:
    doc: 'The coordinates of the genomic region to display, in UCSC notation.example:
      chr1:10,000,000-11,000,000'
    type: string
    inputBinding:
      position: 2
      separate: true
  output:
    doc: Save the image of the contact matrix to file. The figure format is deduced
      from the extension of the file, the supported formats are png, jpg, svg, pdf,
      ps and eps.
    type: string
    inputBinding:
      position: 3
      prefix: -o
      separate: true
outputs:
  out:
    doc: The output image file
    type: File
    outputBinding:
      glob: $(inputs.output)
