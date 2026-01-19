from typing import Optional

from ai_tomator.core.engine.base import BaseEngine
import tiktoken
import openai

from ai_tomator.core.engine.models.engine_health_model import EngineHealth
from ai_tomator.core.engine.models.model_settings_model import ModelSettings
from ai_tomator.core.engine.models.response_model import EngineResponse


class OpenAIEngine(BaseEngine):

    def __init__(self, api_token=None, base_url=None):
        super().__init__(api_token, base_url)
        if base_url is None:
            self.client = openai.Client(api_key=api_token)
        else:
            self.client = openai.Client(api_key=api_token, base_url=base_url)

    def models(self) -> list[str]:
        models = self.client.models.list()
        model_ids = [m.id for m in models.data]
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
            uploaded = self.client.files.create(
                file=open(file_path, "rb"), purpose="input"
            )
            response = self.client.responses.create(
                model=model,
                input=[
                    {"type": "text", "text": prompt},
                    {"type": "input_file", "file_id": uploaded.id},
                ],
                temperature=model_settings.temperature,
            )
        else:
            response = self.client.chat.completions.create(
                model=model,
                temperature=model_settings.temperature,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content},
                ],
                stream=False,
                response_format={"type": "json_object"},
            )

        return EngineResponse(
            engine=self.__class__.__name__,
            model=model,
            temperature=model_settings.temperature,
            top_p=model_settings.top_p,
            top_k=None,
            max_output_tokens=None,
            seed=None,
            context_window=None,
            prompt=prompt,
            input=content or "[Uploaded File]",
            output=response.choices[0].message.content,
            input_tokens=0,
            output_tokens=0,
        )
