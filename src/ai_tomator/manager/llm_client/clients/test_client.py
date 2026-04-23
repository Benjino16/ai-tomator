from typing import Optional

from ai_tomator.manager.file_manager import MediaFile
from ai_tomator.manager.llm_client.clients.base import BaseLLMClient
from ai_tomator.manager.llm_client.models.engine_health_model import EngineHealth
from ai_tomator.manager.llm_client.models.model_settings_model import ModelSettings
from ai_tomator.manager.llm_client.models.response_model import LLMClientResponse

MODELS = ["test_model_pro", "test_model_fast", "test_model_fail"]


class TestLLMClient(BaseLLMClient):
    """
    TestEngine is a mock implementation of BaseEngine.

    It allows users to validate their AI-Tomator setup without needing
    a real API endpoint. All calls are simulated locally and always use
    the predefined test domain (https://test.ai-tomator.local) and token.

    This llm_client ensures that the system’s routing, configuration, and
    llm_client management logic work correctly before connecting to real APIs.
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

    def models(self) -> list[str]:
        return MODELS

    def run(
        self,
        model: str,
        prompt: str,
        file: Optional[MediaFile] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> LLMClientResponse:

        if not file and not content:
            raise ValueError("Either file_path or content must be specified")

        if model not in MODELS:
            raise ValueError(f"Unknown model {model}")

        if model == "test_model_fail":
            raise ValueError("Test model fail")

        response = (
            f"[TEST CLIENT] Response"
            f"using model '{model}' at {self.base_url} "
            f"with token '{self.api_token}'."
            f"Uploaded File: {file.name}"
            if file
            else f"Content: {content}"
        )

        return LLMClientResponse(
            client=self.__class__.__name__,
            model=model,
            temperature=model_settings.temperature,
            json_format=model_settings.json_format,
            top_p=model_settings.top_p,
            top_k=model_settings.top_k,
            max_output_tokens=model_settings.max_output_tokens,
            seed=model_settings.seed,
            context_window=50,
            prompt=prompt,
            input=content or "[Uploaded File]",
            output=response,
            input_tokens=self.token_count(model, prompt),
            output_tokens=self.token_count(model, f"{content} token"),
        )
