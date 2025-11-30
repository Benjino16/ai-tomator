from ai_tomator.core.engine.base import BaseEngine
from ai_tomator.core.engine.models import EngineHealth

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
        temperature: float,
        file_path: str = None,
        content: str = None,
    ) -> str:

        if not file_path and not content:
            raise ValueError("Either file_path or content must be specified")

        if model not in MODELS:
            raise ValueError(f"Unknown model {model}")

        if file_path:
            return (
                f"[TEST ENGINE] Processed file '{file_path}' "
                f"using model '{model}' at {self.base_url} "
                f"with token '{self.api_token}'."
            )

        return (
            f"[TEST ENGINE] Processed content '{content}' "
            f"using model '{model}' at {self.base_url} "
            f"with token '{self.api_token}'."
        )
