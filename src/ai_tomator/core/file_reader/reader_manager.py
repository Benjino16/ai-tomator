from typing import Dict, Tuple, Type
from ai_tomator.core.file_reader.base import BaseFileReader
from ai_tomator.core.file_reader.pypdf2_reader import PyPDF2FileReader
from ai_tomator.core.file_reader.pymupdf_reader import PyMuPDFFileReader


class FileReaderManager:
    """Registry-based manager for file readers."""

    _readers: Dict[str, Tuple[Type[BaseFileReader], str]] = {}

    @classmethod
    def register(cls, reader_cls: Type[BaseFileReader]):
        for mode in reader_cls.modes:
            public_name = f"{reader_cls.base_name}_{mode}".lower()
            cls._readers[public_name] = (reader_cls, mode)

    @classmethod
    def get_supported(cls):
        return list(cls._readers.keys())

    @classmethod
    def read(cls, reader_name: str, file_path: str) -> str:
        reader_name = reader_name.lower()

        if reader_name not in cls._readers:
            raise ValueError(f"Unknown file reader: {reader_name}")

        reader_cls, mode = cls._readers[reader_name]
        return reader_cls().read(file_path, mode)


# register default readers
FileReaderManager.register(PyPDF2FileReader)
FileReaderManager.register(PyMuPDFFileReader)
