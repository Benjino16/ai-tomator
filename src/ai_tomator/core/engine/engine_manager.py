from ai_tomator.core.engine.gemini_engine import GeminiEngine
from ai_tomator.core.engine.openai_engine import OpenAIEngine
from ai_tomator.core.engine.test_engine import TestEngine
from ai_tomator.core.file_reader.reader_manager import FileReaderManager


class EngineManager:
    def __init__(self):
        self.engine_map = {
            "test": TestEngine,
            "gemini": GeminiEngine,
            "openai": OpenAIEngine,
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

    def process(self, endpoint, file_reader, prompt, file_path, model, temperature):
        engine = self._get_engine_instance(endpoint)

        if file_reader == "upload":
            include_file_path = file_path
            content = None
        else:
            include_file_path = None
            content = FileReaderManager.read(file_reader, file_path)

        return engine.run(
            model=model,
            prompt=prompt,
            temperature=temperature,
            content=content,
            file_path=include_file_path,
        )

    def get_engines(self):
        return list(self.engine_map.keys())
