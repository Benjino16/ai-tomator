from abc import ABC, abstractmethod
from typing import List


class FileStorage(ABC):
    @abstractmethod
    def upload(self, file_path: str, content: bytes) -> bool:
        pass

    @abstractmethod
    def download(self, file_path: str) -> bytes:
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
