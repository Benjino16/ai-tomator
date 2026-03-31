from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from ai_tomator.manager.llm_client.models.engine_health_model import EngineHealth
from ai_tomator.manager.llm_client.models.response_model import EngineResponse
from ai_tomator.manager.llm_client.models.model_settings_model import ModelSettings


class BaseLLMClient(ABC):

    def __init__(self, api_token: Optional[str] = None, base_url: Optional[str] = None):
        self.api_token = api_token
        self.base_url = base_url

    @abstractmethod
    def run(
        self,
        model: str,
        prompt: str,
        file: Optional[BinaryIO] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> EngineResponse:
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
