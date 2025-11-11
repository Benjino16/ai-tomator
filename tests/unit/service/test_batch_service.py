import pytest
from unittest.mock import MagicMock, patch
from ai_tomator.service.batch_service import BatchService


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.batches.add = MagicMock()
    db.batches.list = MagicMock(return_value=[{"id": 1}, {"id": 2}])
    yield db


@pytest.fixture
def mock_batch_manager():
    with patch("ai_tomator.service.batch_service.BatchManager") as MockManager:
        batch_manager = MagicMock()
        batch_manager.start_batch.return_value = ""
        batch_manager.stop_batch.return_value = ""
        batch_manager.get_engines.return_value = ["test"]
        batch_manager.get_file_readers.return_value = ["pdf"]
        MockManager.return_value = batch_manager
        yield batch_manager


@pytest.fixture
def mock_file_service():
    with patch("ai_tomator.service.batch_service.FileService") as MockFileService:
        file_service = MagicMock()
        file_service.get_file_path.return_value = ""
        MockFileService.return_value = file_service
        yield file_service


@pytest.fixture
def mock_endpoint_service():
    with patch(
        "ai_tomator.service.batch_service.EndpointService"
    ) as MockEndpointService:
        endpoint_service = MagicMock()
        endpoint_service.get.return_value = {
            "name": "test_endpoint",
            "engine": "test",
            "token": "x",
            "url": "y",
        }
        MockEndpointService.return_value = endpoint_service
        yield endpoint_service


@pytest.fixture
def service(mock_db, mock_batch_manager, mock_endpoint_service, mock_file_service):
    return BatchService(
        db=mock_db,
        batch_manager=mock_batch_manager,
        endpoint_service=mock_endpoint_service,
        file_service=mock_file_service,
    )


def test_start_creates_batch_and_starts_batch(service, mock_db, mock_batch_manager):
    mock_db.batches.add.return_value = {"id": 1, "name": "batch_test"}
    result = service.start(
        prompt="analyze",
        files=["file1.txt"],
        endpoint_name="test_endpoint",
        file_reader="pdf",
        model="gpt-4",
        delay=0.1,
        temperature=0.7,
    )

    mock_db.batches.add.assert_called_once()
    mock_batch_manager.start_batch.assert_called_once()
    assert result["id"] == 1
    assert result["name"] == "batch_test"


def test_start_raises_for_invalid_file(service, mock_file_service):
    mock_file_service.get_file_path.return_value = None

    with pytest.raises(ValueError) as exc:
        service.start(
            prompt="test",
            files=["missing.txt"],
            endpoint_name="test_endpoint",
            file_reader="txt",
            model="gpt-4",
            delay=0.1,
            temperature=0.7,
        )

    assert "Invalid file" in str(exc.value)


def test_stop_calls_batch_manager(service, mock_batch_manager):
    result = service.stop(batch_id=5)
    mock_batch_manager.stop_batch.assert_called_once_with(5)
    assert result == {"batch_id": 5, "status": "stopped"}


def test_list_runs_returns_batches(service, mock_db):
    result = service.list_runs()
    assert isinstance(result, list)
    assert result == [{"id": 1}, {"id": 2}]
    mock_db.batches.list.assert_called_once()


def test_list_engines_returns_values(service, mock_batch_manager):
    result = service.list_engines()
    assert result == ["test"]
    mock_batch_manager.get_engines.assert_called_once()


def test_list_file_readers_returns_values(service, mock_batch_manager):
    result = service.list_file_readers()
    assert result == ["pdf"]
    mock_batch_manager.get_file_readers.assert_called_once()
