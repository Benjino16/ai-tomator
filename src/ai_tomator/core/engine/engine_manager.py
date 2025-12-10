from ai_tomator.core.engine.gemini_engine import GeminiEngine
from ai_tomator.core.engine.models.engine_health_model import EngineHealth
from ai_tomator.core.engine.models.model_settings_model import ModelSettings
from ai_tomator.core.engine.models.response_model import EngineResponse
from ai_tomator.core.engine.ollama_engine import OllamaEngine
from ai_tomator.core.engine.test_engine import TestEngine
from ai_tomator.core.file_reader.reader_manager import FileReaderManager


class EngineManager:
    def __init__(self):
        self.engine_map = {
            "test": TestEngine,
            "gemini": GeminiEngine,
            # "openai": OpenAIEngine,
            "ollama": OllamaEngine,
        }
        self._instances = {}

    def _get_engine_instance(self, endpoint):
        name = endpoint["name"]

        # create the engine only once per endpoint
        if name not in self._instances:
            engine_type = endpoint["engine"]

            if engine_type not in self.engine_map:
                raise ValueError(f"Engine '{engine_type}' not supported.")

            engine_cls = self.engine_map[engine_type]
            self._instances[name] = engine_cls(
                api_token=endpoint["token"],
                base_url=endpoint["url"],
            )
            print("NEW ENGINE CREATED")

        return self._instances[name]

    def process(
        self, endpoint, file_reader, prompt, file_path, model, temperature
    ) -> EngineResponse:
        engine = self._get_engine_instance(endpoint)

        if file_reader == "upload":
            include_file_path = file_path
            content = None
        else:
            include_file_path = None
            content = FileReaderManager.read(file_reader, file_path)

        response: EngineResponse = engine.run(
            model=model,
            prompt=prompt,
            content=content,
            file_path=include_file_path,
            model_settings=ModelSettings(temperature=temperature),
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
        return list(self.engine_map.keys())
