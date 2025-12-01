import pytest
from unittest.mock import MagicMock

from ai_tomator.core.engine.engine_manager import EngineManager
from ai_tomator.manager.endpoint_manager import EndpointManager
from ai_tomator.service.endpoint_service import EndpointService


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.endpoints.add = MagicMock()
    db.endpoints.get = MagicMock(return_value={"name": "x", "engine": "gpt"})
    db.endpoints.list = MagicMock(return_value=[{"name": "x"}])
    db.endpoints.delete = MagicMock()
    return db


@pytest.fixture
def service(mock_db):
    return EndpointService(
        db=mock_db, endpoint_manager=EndpointManager(engine_manager=EngineManager())
    )


def test_add_calls_db_and_returns_status(service, mock_db):
    result = service.add("test", "gpt", "url", "token")
    mock_db.endpoints.add.assert_called_once_with("test", "gpt", "url", "token")
    assert result == {"name": "test", "engine": "gpt", "status": "added"}


def test_get_returns_endpoint(service, mock_db):
    result = service.get("x")
    mock_db.endpoints.get.assert_called_once_with("x", False)
    assert result == {"name": "x", "engine": "gpt"}


def test_list_returns_all(service, mock_db):
    result = service.list()
    mock_db.endpoints.list.assert_called_once()
    assert result == [{"name": "x"}]


def test_delete_calls_db_and_returns_status(service, mock_db):
    result = service.delete("x")
    mock_db.endpoints.delete.assert_called_once_with("x")
    assert result == {"name": "x", "status": "deleted"}
