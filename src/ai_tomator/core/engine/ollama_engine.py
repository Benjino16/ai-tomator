from typing import Optional

from ai_tomator.core.engine.base import BaseEngine
from ai_tomator.core.engine.models.engine_health_model import EngineHealth
import tiktoken
from ollama import Client, ChatResponse

from ai_tomator.core.engine.models.model_settings_model import ModelSettings
from ai_tomator.core.engine.models.response_model import EngineResponse


class OllamaEngine(BaseEngine):

    def __init__(self, api_token=None, base_url=None):
        super().__init__(api_token, base_url)
        if base_url is None:
            self.client: Client = Client()
        else:
            self.client: Client = Client(base_url)

    def models(self) -> list[str]:
        models = self.client.list().models
        model_ids = [m.model for m in models]
        return model_ids

    def health(self) -> EngineHealth:
        try:
            self.models()
            return EngineHealth(True)
        except Exception as e:
            return EngineHealth(False, e.__str__())

    def token_count(self, model: str, text: str) -> int:
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    def cost_estimate(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        return 0  # todo: implement price calculation

    def time_estimate(self, model: str, tokens: int) -> float:
        return tokens / 150  # todo: implement real statistic

    def run(
        self,
        model: str,
        prompt: str,
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> EngineResponse:
        if file_path is None and content is None:
            raise ValueError("Either file_path or content must be specified")

        if file_path:
            raise ValueError(
                "Ollama engine does not support file uploads. Please use a file reader instead."
            )
        else:
            response: ChatResponse = self.client.chat(
                model=model,
                keep_alive=0,
                options={"temperature": model_settings.temperature},
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": content,
                    },
                ],
            )
            return EngineResponse(
                engine=self.__class__.__name__,
                model=model,
                temperature=model_settings.temperature,
                top_p=model_settings.top_p,
                top_k=model_settings.top_k,
                max_output_tokens=model_settings.max_output_tokens,
                seed=model_settings.seed,
                context_window=None,
                prompt=prompt,
                input=content or "[Uploaded File]",
                output=response.message.content,
                input_tokens=response.prompt_eval_count,
                output_tokens=response.eval_count,
            )
