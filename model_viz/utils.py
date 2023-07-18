from PyPDF2 import PdfMerger
from typing import List


def merge_pdf_files(files: List[str], output_file: str) -> None:
    """Merge multiple PDF files into one PDF file

    Args:
        files (list): List of PDF files to merge
        output_file (str): Output file name
    """

    merger = PdfMerger()
    for file in files:
        merger.append(file)
    merger.write(output_file)
    merger.close()
