import base64
from typing import Optional

import anthropic
from anthropic import APIStatusError

from ai_tomator.manager.file_manager import MediaFile
from ai_tomator.manager.llm_client.clients.base import BaseLLMClient
from ai_tomator.manager.llm_client.models.engine_health_model import EngineHealth
from ai_tomator.manager.llm_client.models.exceptions import RateLimitError
from ai_tomator.manager.llm_client.models.model_settings_model import ModelSettings
from ai_tomator.manager.llm_client.models.response_model import LLMClientResponse


class AnthropicLLMClient(BaseLLMClient):

    def __init__(self, api_token=None, base_url=None):
        super().__init__(api_token, base_url)
        self.client = anthropic.Anthropic(api_key=api_token)

    def models(self) -> list[str]:
        models = self.client.models.list()
        return [m.id for m in models.data]

    def health(self) -> EngineHealth:
        try:
            self.models()
            return EngineHealth(True)
        except Exception as e:
            return EngineHealth(False, str(e))

    def token_count(self, model: str, text: str) -> int:
        response = self.client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": text}],
        )
        return response.input_tokens

    def run(
        self,
        model: str,
        prompt: str,
        file: Optional[MediaFile] = None,
        content: Optional[str] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> LLMClientResponse:
        if file is None and content is None:
            raise ValueError("Either file or content must be specified")

        if file:
            encoded = base64.standard_b64encode(file.data).decode("utf-8")
            user_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image",  # für PDFs: "type": "document"
                    "source": {
                        "type": "base64",
                        "media_type": file.mime_type,
                        "data": encoded,
                    },
                },
            ]
        else:
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "text", "text": content},
            ]

        system_prompt = (
            "Respond only with valid JSON. No explanation, no markdown."
            if model_settings.json_format
            else None
        )

        kwargs = {
            "model": model,
            "max_tokens": model_settings.max_output_tokens or 4096,
            "messages": [{"role": "user", "content": user_content}],
            "temperature": model_settings.temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if model_settings.top_p is not None:
            kwargs["top_p"] = model_settings.top_p
        if model_settings.top_k is not None:
            kwargs["top_k"] = model_settings.top_k

        try:
            response = self.client.messages.create(**kwargs)
        except APIStatusError as e:
            if e.status_code == 429:
                raise RateLimitError(e)
            raise

        output_text = response.content[0].text

        return LLMClientResponse(
            client=self.__class__.__name__,
            model=model,
            temperature=model_settings.temperature,
            json_format=model_settings.json_format,
            top_p=model_settings.top_p,
            top_k=model_settings.top_k,
            max_output_tokens=model_settings.max_output_tokens,
            seed=model_settings.seed,
            context_window=None,
            prompt=prompt,
            input=content or "[Uploaded File]",
            output=output_text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
