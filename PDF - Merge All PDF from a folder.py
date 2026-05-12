#this code allows you to merge all pdf that are in a folder
import os
from PyPDF2 import PdfFileMerger
source_dir=os.getcwd() #get the current working directory

merger = PdfFileMerger()

for item in os.listdir(source_dir):
    if item.endswith('pdf'):
        merger.append(item)

merger.write("complete.pdf")
merger.close