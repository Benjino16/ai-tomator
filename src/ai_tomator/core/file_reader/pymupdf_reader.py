import re
import pymupdf
from ai_tomator.core.file_reader.base import BaseFileReader


class PyMuPDFFileReader(BaseFileReader):
    base_name = "pymupdf"

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
        text = ""
        doc = pymupdf.open(file_path)
        for page in doc:
            text += page.get_text()
        return text

    def _remove_urls(self, text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)
