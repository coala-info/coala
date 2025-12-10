cwlVersion: v1.2
class: CommandLineTool
baseCommand: ""
requirements:
- class: DockerRequirement
  dockerPull: pdftk/pdftk:latest
- class: InlineJavascriptRequirement
label: pdftk_cat
doc: Join or remove pages from one or two PDF files using pdftk cat operation
inputs:
  input_pdf1:
    label: input_pdf1
    doc: First input PDF file
    type: File
    inputBinding:
      position: 1
  input_pdf2:
    label: input_pdf2
    doc: Second input PDF file (optional, for joining two PDFs)
    type: File?
    inputBinding:
      position: 2
  page_ranges:
    label: page_ranges
    doc: |
      Page ranges for cat operation. Examples:
      - Single file: "1-12 14-end" (removes page 13) or "1-21" (specific range)
      - Two files with handles: "A1-10 B5-15" (requires input files to use handles A= and B=)
      - Two files all pages: omit this parameter
      If omitted, all pages from all input files are used.
      Note: For two files with different page ranges, you may need to use handles (A=file1.pdf B=file2.pdf format).
    type: string?
  output_filename:
    label: output_filename
    doc: Output PDF filename
    type: string
    default: output.pdf
    inputBinding:
      prefix: output
      position: 5
      separate: true
arguments:
- valueFrom: cat
  position: 3
- valueFrom: |
    ${
      if (inputs.page_ranges) {
        // Split page ranges by spaces and add each as separate argument
        var ranges = inputs.page_ranges.trim().split(/\s+/);
        return ranges;
      }
      return [];
    }
  position: 4
outputs:
  output_pdf:
    label: output_pdf
    doc: Output PDF file with joined or filtered pages
    type: File
    outputBinding:
      glob: $(inputs.output_filename)
$rud:
  author: cmdagent team
  date: 2024
  url: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/
  example:
    - Join two PDFs: |
        input_pdf1: file1.pdf
        input_pdf2: file2.pdf
        output_filename: merged.pdf
    - Remove page 13 from a PDF: |
        input_pdf1: input.pdf
        page_ranges: "1-12 14-end"
        output_filename: output.pdf
    - Join specific pages from a single PDF: |
        input_pdf1: input.pdf
        page_ranges: "1-10 20-30"
        output_filename: selected.pdf
