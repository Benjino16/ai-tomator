from typing import Dict, Type
from ai_tomator.core.file_reader.pdf_reader import PDFReader


class FileReaderManager:
    """Registry-based manager for file readers."""

    _readers: Dict[str, Type] = {}

    @classmethod
    def register(cls, reader_cls):
        cls._readers[reader_cls.name.lower()] = reader_cls

    @classmethod
    def get_supported(cls):
        return list(cls._readers.keys())

    @classmethod
    def read(cls, reader_name: str, file_path: str) -> str:
        reader_name = reader_name.lower()
        if reader_name not in cls._readers:
            raise ValueError(f"Unknown file reader: {reader_name}")
        return cls._readers[reader_name]().read(file_path)


# register default readers
FileReaderManager.register(PDFReader)
