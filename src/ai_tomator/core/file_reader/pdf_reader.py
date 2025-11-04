from PyPDF2 import PdfReader
from ai_tomator.core.file_reader.base import BaseFileReader


class PDFReader(BaseFileReader):
    name = "pypdf2"

    def read(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
