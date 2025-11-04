from typing import Protocol

class BaseFileReader(Protocol):
    """Common interface for all file readers."""
    name: str

    def read(self, file_path: str) -> str:
        ...
