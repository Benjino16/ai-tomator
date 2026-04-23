from abc import ABC, abstractmethod
from typing import List, BinaryIO


class FileStorage(ABC):
    @abstractmethod
    def upload(self, file_path: str, content: BinaryIO, length: int) -> bool:
        pass

    @abstractmethod
    def download(self, file_path: str) -> BinaryIO:
        pass

    @abstractmethod
    def delete(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def list(self, prefix: str = "") -> List[str]:
        pass
