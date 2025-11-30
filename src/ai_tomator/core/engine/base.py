from abc import ABC, abstractmethod
from typing import Optional
from .models import EngineHealth


class BaseEngine(ABC):

    def __init__(self, api_token: Optional[str] = None, base_url: Optional[str] = None):
        self.api_token = api_token
        self.base_url = base_url

    @abstractmethod
    def run(
        self,
        model: str,
        prompt: str,
        temperature: float,
        file_path: Optional[str] = None,
        content: Optional[str] = None,
    ) -> str:
        pass

    @abstractmethod
    def models(self) -> list[str]:
        pass

    @abstractmethod
    def health(self) -> EngineHealth:
        pass

    @abstractmethod
    def token_count(self, model: str, text: str) -> int:
        pass

    @abstractmethod
    def cost_estimate(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        pass

    @abstractmethod
    def time_estimate(self, model: str, tokens: int) -> float:
        pass
