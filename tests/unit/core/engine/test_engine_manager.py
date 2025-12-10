import pytest
from unittest.mock import patch
from ai_tomator.core.engine.engine_manager import EngineManager
from ai_tomator.core.engine.models.response_model import EngineResponse


class MockEngine:
    def __init__(self, api_token, base_url):
        self.api_token = api_token
        self.base_url = base_url

    def run(self, model, prompt, content, file_path, model_settings):
        return EngineResponse(
            model=model,
            prompt=prompt,
            temperature=model_settings.temperature,
            output=content,
            engine="Test Engine",
            input=content or f"[Uploaded File: {file_path}]",
            input_tokens=0,
            output_tokens=0,
            top_k=None,
            top_p=None,
            max_output_tokens=None,
            seed=None,
            context_window=None,
        )


@pytest.fixture
def engine_manager():
    em = EngineManager()
    em.engine_map = {"mock": MockEngine}
    return em


@patch(
    "ai_tomator.core.engine.engine_manager.FileReaderManager.read",
    return_value="file content",
)
def test_process_with_file_content(mock_read, engine_manager):
    endpoint = {
        "name": "test_endpoint",
        "engine": "mock",
        "token": "abc123",
        "url": "http://example.com",
    }
    result = engine_manager.process(
        endpoint=endpoint,
        file_reader="text",
        prompt="Test prompt",
        file_path="path/to/file.txt",
        model="gpt-test",
        temperature=0.5,
    )

    mock_read.assert_called_once_with("text", "path/to/file.txt")
    assert result.output == "file content"
    assert result.model == "gpt-test"


def test_process_with_upload(engine_manager):
    endpoint = {
        "name": "test_endpoint",
        "engine": "mock",
        "token": "abc123",
        "url": "http://example.com",
    }
    result = engine_manager.process(
        endpoint=endpoint,
        file_reader="upload",
        prompt="Another test",
        file_path="path/to/upload.txt",
        model="gpt-test",
        temperature=1.0,
    )

    assert result.input == "[Uploaded File: path/to/upload.txt]"
    assert result.prompt == "Another test"


def test_invalid_engine_raises(engine_manager):
    endpoint = {
        "name": "test_endpoint",
        "engine": "invalid",
        "token": "123",
        "url": "x",
    }
    with pytest.raises(ValueError) as e:
        engine_manager.process(endpoint, "text", "prompt", "file.txt", "model", 0.2)
    assert "not supported" in str(e.value)


def test_get_engines(engine_manager):
    engines = list(engine_manager.get_engines())
    assert engines == ["mock"]
