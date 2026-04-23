from ai_tomator.manager.file_manager import MediaFile
from ai_tomator.manager.llm_client.clients.gemini_client import GeminiLLMClient
from ai_tomator.manager.llm_client.models.engine_health_model import EngineHealth
from ai_tomator.manager.llm_client.models.model_settings_model import ModelSettings
from ai_tomator.manager.llm_client.models.response_model import LLMClientResponse
from ai_tomator.manager.llm_client.clients.openai_client import OpenAILLMClient
from ai_tomator.manager.llm_client.clients.ollama_client import OllamaLLMClient
from ai_tomator.manager.llm_client.clients.test_client import TestLLMClient
from ai_tomator.manager.file_reader.reader_manager import FileReaderManager


class ClientManager:
    def __init__(self):
        self.client_map = {
            "test": TestLLMClient,
            "gemini": GeminiLLMClient,
            "openai": OpenAILLMClient,
            "ollama": OllamaLLMClient,
        }
        self._instances = {}

    def _get_engine_instance(self, endpoint):
        name = endpoint["name"]

        # create the llm_client only once per endpoint
        if name not in self._instances:
            client_type = endpoint["client"]

            if client_type not in self.client_map:
                raise ValueError(f"Engine '{client_type}' not supported.")

            client_cls = self.client_map[client_type]
            self._instances[name] = client_cls(
                api_token=endpoint["token"],
                base_url=endpoint["url"],
            )

        return self._instances[name]

    def process(
        self,
        endpoint,
        file_reader,
        prompt,
        file: MediaFile,
        model,
        temperature,
        json_format,
    ) -> LLMClientResponse:
        engine = self._get_engine_instance(endpoint)

        if file_reader == "upload":
            include_file = file
            content = None
        else:
            include_file = None
            content = FileReaderManager.read(file_reader, file.data)

        response: LLMClientResponse = engine.run(
            model=model,
            prompt=prompt,
            content=content,
            file=include_file,
            model_settings=ModelSettings(
                temperature=temperature, json_format=json_format
            ),
        )
        return response

    def endpoint_health(self, endpoint) -> EngineHealth:
        engine = self._get_engine_instance(endpoint)
        return engine.health()

    def endpoint_models(self, endpoint):
        engine = self._get_engine_instance(endpoint)
        return engine.models()

    def endpoint_time_estimate(self, endpoint, model: str, tokens: int):
        engine = self._get_engine_instance(endpoint)
        return engine.time_estimate(model, tokens)

    def endpoint_token_count(self, endpoint, model: str, text: str):
        engine = self._get_engine_instance(endpoint)
        return engine.token_count(model, text)

    def endpoint_cost_estimate(
        self, endpoint, model: str, prompt_tokens: int, completion_tokens: int
    ):
        engine = self._get_engine_instance(endpoint)
        return engine.token_count(model, prompt_tokens, completion_tokens)

    def get_engines(self):
        return list(self.client_map.keys())
