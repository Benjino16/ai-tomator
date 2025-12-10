from typing import Optional

from ai_tomator.core.engine.base import BaseEngine
from ai_tomator.core.engine.models.engine_health_model import EngineHealth
from ai_tomator.core.engine.models.model_settings_model import ModelSettings
from ai_tomator.core.engine.models.response_model import EngineResponse

MODELS = ["test_model_pro", "test_model_fast"]


class TestEngine(BaseEngine):
    """
    TestEngine is a mock implementation of BaseEngine.

    It allows users to validate their AI-Tomator setup without needing
    a real API endpoint. All calls are simulated locally and always use
    the predefined test domain (https://test.ai-tomator.local) and token.

    This engine ensures that the system’s routing, configuration, and
    engine management logic work correctly before connecting to real APIs.
    """

    def health(self) -> EngineHealth:
        if self.base_url == "https://test.ai-tomator.local":
            return EngineHealth(True)
        else:
            return EngineHealth(
                False, "Could not establish API connection to URL: " + self.base_url
            )

    def token_count(self, model: str, text: str) -> int:
        return text.count(" ")

    def cost_estimate(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        if model == "test_model_pro":
            return prompt_tokens / 200000 + completion_tokens / 200000
        elif model == "test_model_fast":
            return prompt_tokens / 400000 + completion_tokens / 400000
        else:
            raise ValueError(f"Unknown model: {model}")

    def time_estimate(self, model: str, tokens: int) -> float:
        if model == "test_model_pro":
            return tokens / 100
        elif model == "test_model_fast":
            return tokens / 1000
        else:
            raise ValueError(f"Unknown model: {model}")

    def models(self) -> list[str]:
        return MODELS

    def run(
        self,
        model: str,
        prompt: str,
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> EngineResponse:

        if not file_path and not content:
            raise ValueError("Either file_path or content must be specified")

        if model not in MODELS:
            raise ValueError(f"Unknown model {model}")

        response = (
            f"[TEST ENGINE] Response"
            f"using model '{model}' at {self.base_url} "
            f"with token '{self.api_token}'."
            f"{"File Path: " + file_path if file_path else "Content: " + content}"
        )

        return EngineResponse(
            engine = self.__class__.__name__,
            model = model,
            temperature = model_settings.temperature,
            top_p = model_settings.top_p,
            top_k = model_settings.top_k,
            max_output_tokens= model_settings.max_output_tokens,
            seed = model_settings.seed,
            context_window = 50,
            prompt = prompt,
            input = content or "[Uploaded File]",
            output = response,
            input_tokens=self.token_count(model, prompt),
            output_tokens=self.token_count(model, content + ""),
        )
