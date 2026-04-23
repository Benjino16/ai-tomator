from typing import Optional

from ai_tomator.manager.file_manager import MediaFile
from ai_tomator.manager.llm_client.clients.base import BaseLLMClient
import tiktoken
import openai

from ai_tomator.manager.llm_client.models.engine_health_model import EngineHealth
from ai_tomator.manager.llm_client.models.exceptions import RateLimitError
from ai_tomator.manager.llm_client.models.model_settings_model import ModelSettings
from ai_tomator.manager.llm_client.models.response_model import LLMClientResponse


class OpenAILLMClient(BaseLLMClient):

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

    def run(
        self,
        model: str,
        prompt: str,
        file: Optional[MediaFile] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> LLMClientResponse:
        if file is None and content is None:
            raise ValueError("Either file_path or content must be specified")

        text_format = (
            {"format": {"type": "json_object"}}
            if model_settings.json_format
            else {"format": {"type": "text"}}
        )
        response_format = (
            {"type": "json_object"} if model_settings.json_format else {"type": "text"}
        )
        try:
            if file:
                uploaded = self.client.files.create(
                    file=(file.name, file.data), purpose="user_data"
                )
                response = self.client.responses.create(  # type: ignore
                    model=model,
                    input=[
                        {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_file", "file_id": uploaded.id},
                            ],
                        }
                    ],
                    temperature=model_settings.temperature,
                    stream=False,
                    text=text_format,
                )
                result_text = response.output_text
            else:
                response = self.client.chat.completions.create(  # type: ignore
                    model=model,
                    temperature=model_settings.temperature,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": content},
                    ],
                    stream=False,
                    response_format=response_format,
                )
                result_text = response.choices[0].message.content
        except openai.RateLimitError as e:
            raise RateLimitError(e)

        return LLMClientResponse(
            client=self.__class__.__name__,
            model=model,
            temperature=model_settings.temperature,
            json_format=model_settings.json_format,
            top_p=model_settings.top_p,
            top_k=None,
            max_output_tokens=None,
            seed=None,
            context_window=None,
            prompt=prompt,
            input=content or "[Uploaded File]",
            output=result_text,
            input_tokens=0,
            output_tokens=0,
        )
