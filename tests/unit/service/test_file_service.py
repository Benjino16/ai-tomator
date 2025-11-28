import pytest
from unittest.mock import MagicMock
from ai_tomator.service.file_service import FileService


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.files.list = MagicMock(return_value=["a.txt", "b.txt"])
    return db


@pytest.fixture
def mock_file_manager():
    fm = MagicMock()
    fm.save = MagicMock(return_value={"storage_name": "saved.txt", "display_name": "display_file.txt", "tags": ["tag1", "tag2"]})
    fm.delete = MagicMock(return_value=True)
    fm.get_path = MagicMock(return_value="/tmp/saved.txt")
    return fm


@pytest.fixture
def service(mock_db, mock_file_manager):
    return FileService(db=mock_db, file_manager=mock_file_manager)


def test_upload_file_calls_file_manager(service, mock_file_manager):
    result = service.upload_file(file="mock_file", tags=["tag"])
    mock_file_manager.save.assert_called_once_with("mock_file", ["tag"])
    assert result == {"storage_name": "saved.txt", "display_name": "display_file.txt", "tags": ["tag1", "tag2"]}


def test_list_files_returns_from_db(service, mock_db):
    result = service.list_files()
    mock_db.files.list.assert_called_once()
    assert result == ["a.txt", "b.txt"]


def test_delete_file_success(service, mock_file_manager):
    result = service.delete_file("a.txt")
    mock_file_manager.delete.assert_called_once_with("a.txt")
    assert result == {"filename": "a.txt", "status": "deleted"}


def test_delete_file_not_found(service, mock_file_manager):
    mock_file_manager.delete.return_value = False
    with pytest.raises(FileNotFoundError):
        service.delete_file("missing.txt")


def test_get_file_path_returns_path(service, mock_file_manager):
    result = service.get_file_path("a.txt")
    mock_file_manager.get_path.assert_called_once_with("a.txt")
    assert result == "/tmp/saved.txt"
