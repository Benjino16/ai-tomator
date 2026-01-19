from typing import Protocol, Iterable


class BaseFileReader(Protocol):
    """Common interface for all file readers."""

    base_name: str
    modes: Iterable[str]
    default_mode: str

    def read(self, file_path: str, mode: str) -> str: ...
