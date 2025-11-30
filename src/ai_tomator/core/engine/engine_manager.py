from ai_tomator.core.engine.gemini_engine import GeminiEngine
from ai_tomator.core.engine.test_engine import TestEngine
from ai_tomator.core.file_reader.reader_manager import FileReaderManager


class EngineManager:
    def __init__(self):
        self.engine_map = {"test": TestEngine, "gemini": GeminiEngine}

    def process(
        self,
        endpoint: dict,
        file_reader: str,
        prompt: str,
        file_path: str,
        model: str,
        temperature: float,
    ):
        engine_type = endpoint["engine"]

        if engine_type not in self.engine_map:
            raise ValueError(f"Engine '{engine_type}' not supported.")

        engine_cls = self.engine_map[engine_type]  # class reference
        engine = engine_cls(api_token=endpoint["token"], base_url=endpoint["url"])

        include_file_path = None
        content = None

        if file_reader == "upload":
            include_file_path = file_path
        else:
            content = FileReaderManager.read(file_reader, file_path)

        result = engine.run(
            model=model,
            prompt=prompt,
            temperature=temperature,
            content=content,
            file_path=include_file_path,
        )

        return result

    def get_engines(self):
        return list(self.engine_map.keys())
