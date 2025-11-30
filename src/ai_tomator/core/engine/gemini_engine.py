from ai_tomator.core.engine.base import BaseEngine
import tiktoken
from google import genai

from ai_tomator.core.engine.models import EngineHealth


class GeminiEngine(BaseEngine):

    def __init__(self, api_token=None, base_url=None):
        super().__init__(api_token, base_url)
        self.client = genai.Client(api_key=api_token)

    def models(self) -> list[str]:
        models = self.client.models.list()
        model_ids = [m.name for m in models]
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

    def cost_estimate(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        return 0 #todo: implement price calculation

    def time_estimate(self, model: str, tokens: int) -> float:
        return tokens / 150 #todo: implement real statistic

    def run(
            self,
            model: str,
            prompt: str,
            temperature: float,
            file_path: str = None,
            content: str = None,
    ):
        if file_path is None and content is None:
            raise ValueError("Either file_path or content must be specified")

        if file_path:
            file = self.client.files.upload(file=file_path)
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"file_data": {"file_uri": file.uri}},
                        {"text": prompt},
                    ],
                }
            ]
        else:
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt + content},
                    ],
                }
            ]
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config={"temperature": temperature},
        )
        return response.text