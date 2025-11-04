from abc import ABC, abstractmethod

class BaseEngine(ABC):
    @abstractmethod
    def run(
            self,
            model: str,
            prompt: str,
            temperature: float,
            file_path: str = None,
            content: str = None
    ):
        pass