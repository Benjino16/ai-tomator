from ai_tomator.core.engine.test_engine import TestEngine
from ai_tomator.core.file_reader import read_file

class EngineManager:
    def __init__(self):
        self.engine_map = {
            "test": TestEngine
        }

    def process(self, endpoint: dict, file_reader: str, prompt: str, file_path: str, model: str, temperature: float):
        engine_type = endpoint["engine"]

        if engine_type not in self.engine_map:
            raise ValueError(f"Engine '{engine_type}' not supported.")

        engine_cls = self.engine_map[engine_type] #class reference
        engine = engine_cls(api_token=endpoint["token"], base_url=endpoint["url"])

        include_file_path = None
        content = None

        if file_reader == "upload":
            include_file_path = file_path
        else:
            content = read_file(file_reader, file_path)

        result = engine.run(model=model, prompt=prompt, temperature=temperature, content=content, file_path=include_file_path)

        return result

    def get_engines(self):
        return self.engine_map.keys()