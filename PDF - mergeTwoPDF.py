#Below, we want to merge two PDF files named file1 and file2.
#We will name this merged file as #merged.pdf.  You can find
#my file1, file2 and some other pdf files here. But you can use
#any pdf  #file.
#install PyPDF2 library first
from PyPDF2 import PdfFileReader, PdfFileMerger
pdf_file1 = PdfFileReader("file1.pdf")
pdf_file2 = PdfFileReader("file2.pdf")
output = PdfFileMerger()
output.append(pdf_file1)
output.append(pdf_file2)
with open("merged.pdf", "wb") as output_stream:
    output.write(output_stream)