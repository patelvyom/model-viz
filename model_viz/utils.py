from PyPDF2 import PdfMerger
from typing import List
import os


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


def delete_files(files: List[str], delete_dir=False) -> None:
    """Delete files

    Args:
        files (list): List of files to delete
    """
    for file in files:
        os.remove(file)
    if delete_dir:
        os.rmdir(os.path.dirname(files[0]))
