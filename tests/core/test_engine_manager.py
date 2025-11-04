import pytest
from unittest.mock import patch, MagicMock
from ai_tomator.core.engine_manager import EngineManager

class MockEngine:
    def __init__(self, api_token, base_url):
        self.api_token = api_token
        self.base_url = base_url

    def run(self, model, prompt, temperature, content, file_path):
        return {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "content": content,
            "file_path": file_path,
            "token": self.api_token,
            "url": self.base_url,
        }

@pytest.fixture
def engine_manager():
    em = EngineManager()
    em.engine_map = {"mock": MockEngine}
    return em

@patch("ai_tomator.core.engine_manager.read_file", return_value="file content")
def test_process_with_file_content(mock_read, engine_manager):
    endpoint = {"engine": "mock", "token": "abc123", "url": "http://example.com"}
    result = engine_manager.process(
        endpoint=endpoint,
        file_reader="text",
        prompt="Test prompt",
        file_path="path/to/file.txt",
        model="gpt-test",
        temperature=0.5
    )

    mock_read.assert_called_once_with("text", "path/to/file.txt")
    assert result["content"] == "file content"
    assert result["file_path"] is None
    assert result["model"] == "gpt-test"

def test_process_with_upload(engine_manager):
    endpoint = {"engine": "mock", "token": "abc123", "url": "http://example.com"}
    result = engine_manager.process(
        endpoint=endpoint,
        file_reader="upload",
        prompt="Another test",
        file_path="path/to/upload.txt",
        model="gpt-test",
        temperature=1.0
    )

    assert result["file_path"] == "path/to/upload.txt"
    assert result["content"] is None
    assert result["prompt"] == "Another test"

def test_invalid_engine_raises(engine_manager):
    endpoint = {"engine": "invalid", "token": "123", "url": "x"}
    with pytest.raises(ValueError) as e:
        engine_manager.process(endpoint, "text", "prompt", "file.txt", "model", 0.2)
    assert "not supported" in str(e.value)

def test_get_engines(engine_manager):
    engines = list(engine_manager.get_engines())
    assert engines == ["mock"]
