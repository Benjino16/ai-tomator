import re
from PyPDF2 import PdfReader
from ai_tomator.core.file_reader.base import BaseFileReader


class PDFReader(BaseFileReader):
    base_name = "pypdf2"

    modes = (
        "default",
        "remove_urls",
    )

    default_mode = "default"

    def read(self, file_path: str, mode: str) -> str:
        text = self._read_pdf(file_path)

        if mode == "remove_urls":
            text = self._remove_urls(text)

        return text.strip()

    def _read_pdf(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            return "".join(page.extract_text() or "" for page in reader.pages)

    def _remove_urls(self, text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)
