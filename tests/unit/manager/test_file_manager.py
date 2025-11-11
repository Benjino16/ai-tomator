import io
import os
import shutil
import tempfile
import pytest
from unittest.mock import MagicMock
from fastapi import UploadFile
from ai_tomator.manager.file_manager import FileManager


@pytest.fixture
def temp_dir():
    """Creates a temporary directory for file storage."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.fixture
def mock_db():
    """Mock Database object with files sub-ops."""
    db = MagicMock()
    db.files.add = MagicMock()
    db.files.delete = MagicMock()
    db.files.list = MagicMock(return_value=[])
    return db


def make_upload_file(name="example.txt", content=b"data"):
    """Create a dummy UploadFile with in-memory bytes."""
    return UploadFile(filename=name, file=io.BytesIO(content), size=len(content))


def test_unique_name_generates_different_names(temp_dir, mock_db):
    fm = FileManager(temp_dir, mock_db)
    a = fm._unique_name("file.txt")
    b = fm._unique_name("file.txt")
    assert a != b
    assert a.endswith(".txt")


def test_save_creates_file_and_calls_db(temp_dir, mock_db):
    fm = FileManager(temp_dir, mock_db)
    upload = make_upload_file()

    name = fm.save(upload, tags=["tag1"])
    path = os.path.join(temp_dir, name)

    assert os.path.exists(path)
    mock_db.files.add.assert_called_once()
    args, kwargs = mock_db.files.add.call_args
    assert args[0] == name  # storage name


def test_delete_existing_file(temp_dir, mock_db):
    fm = FileManager(temp_dir, mock_db)
    test_file = os.path.join(temp_dir, "delete_me.txt")
    with open(test_file, "w") as f:
        f.write("remove")

    result = fm.delete("delete_me.txt")
    assert result is True
    assert not os.path.exists(test_file)
    mock_db.files.delete.assert_called_once_with("delete_me.txt")


def test_delete_missing_file(temp_dir, mock_db):
    fm = FileManager(temp_dir, mock_db)
    result = fm.delete("notfound.txt")
    assert result is False
    mock_db.files.delete.assert_not_called()


def test_list_files_sorted(temp_dir, mock_db):
    fm = FileManager(temp_dir, mock_db)
    open(os.path.join(temp_dir, "b.txt"), "w").close()
    open(os.path.join(temp_dir, "a.txt"), "w").close()
    assert fm.list_files() == ["a.txt", "b.txt"]


def test_get_path_valid_and_invalid(temp_dir, mock_db):
    fm = FileManager(temp_dir, mock_db)
    test_file = os.path.join(temp_dir, "exists.txt")
    open(test_file, "w").close()
    assert fm.get_path("exists.txt") == test_file

    with pytest.raises(FileNotFoundError):
        fm.get_path("missing.txt")


def test_sync_storage_with_db_add_and_delete(temp_dir, mock_db):
    fm = FileManager(temp_dir, mock_db)

    # file exists on disk but not in db
    open(os.path.join(temp_dir, "new.txt"), "w").close()
    mock_db.files.list.return_value = [{"storage_name": "old.txt"}]

    fm.sync_storage_with_db()

    # should add new.txt and delete old.txt
    mock_db.files.add.assert_called_once()
    mock_db.files.delete.assert_called_once_with(storage_name="old.txt")
