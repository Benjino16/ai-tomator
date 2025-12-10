import pytest
import threading
from unittest.mock import MagicMock, patch

from ai_tomator.core.engine.models.response_model import EngineResponse
from ai_tomator.manager.batch_manager import BatchManager
from ai_tomator.manager.database.models.batch import BatchStatus, BatchFileStatus


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.batches.update_status = MagicMock()
    db.batches.update_batch_file_status = MagicMock()
    db.batches.add_batch_log = MagicMock()
    db.batches.add_file_log = MagicMock()
    db.batches.list = MagicMock(return_value=[{"id": 1}, {"id": 2}])
    db.results.save = MagicMock()
    return db


@pytest.fixture
def mock_engine():
    with patch("ai_tomator.manager.batch_manager.EngineManager") as MockEngine:
        instance = MockEngine.return_value
        instance.process.return_value = "mocked_result"
        instance.get_engines.return_value = ["test"]
        yield instance


@pytest.fixture
def mock_file_reader():
    with patch("ai_tomator.manager.batch_manager.FileReaderManager") as MockFRM:
        MockFRM.get_supported.return_value = ["pdf"]
        yield MockFRM


def test_start_batch_local_thread_start(mock_db, mock_engine, mock_file_reader):
    manager = BatchManager(db=mock_db, engine_manger=mock_engine)

    file_infos = [{"path": "test.txt", "storage_name": "test.txt"}]
    endpoint = {"engine": "test", "token": "x", "url": "y"}

    manager.start_batch(
        batch_id=1,
        file_infos=file_infos,
        endpoint=endpoint,
        file_reader="upload",
        model="gpt",
        prompt="Say hi",
        delay=0.01,
        temperature=0.5,
    )

    assert 1 in manager.active_batches
    assert isinstance(manager.active_batches[1], threading.Thread)


def test_run_batch_flow(mock_db, mock_engine, mock_file_reader):
    """Validate the internal _run_batch logic without real threads."""
    manager = BatchManager(db=mock_db, engine_manger=mock_engine)
    stop_flag = MagicMock()
    stop_flag.is_set.return_value = False
    mock_engine.process.return_value = EngineResponse(
        model="test",
        prompt="test prompt",
        temperature=0.0,
        output="output text",
        engine="Test Engine",
        input="input text",
        input_tokens=0,
        output_tokens=0,
        top_k=None,
        top_p=None,
        max_output_tokens=None,
        seed=None,
        context_window=None,
)

    file_infos = [{"path": "file.txt", "storage_name": "file.txt"}]
    endpoint = {"name": "endpoint", "engine": "test", "token": "abc", "url": "http://x"}

    manager._run_batch(
        batch_id=5,
        file_infos=file_infos,
        endpoint=endpoint,
        file_reader="upload",
        model="mock",
        prompt="hi",
        delay=0,
        temperature=0.3,
        stop_flag=stop_flag,
    )

    # Database calls should occur in expected order
    mock_db.batches.update_status.assert_any_call(
        batch_id=5, status=BatchStatus.RUNNING
    )
    mock_db.batches.update_batch_file_status.assert_any_call(
        batch_id=5, storage_name="file.txt", status=BatchFileStatus.COMPLETED
    )
    mock_db.results.save.assert_called_once_with(
        5, "file.txt", engine_response=mock_engine.process.return_value
    )
    mock_db.batches.update_status.assert_any_call(5, BatchStatus.COMPLETED)


def test_stop_batch(mock_db, mock_engine):
    manager = BatchManager(mock_db, engine_manger=mock_engine)
    fake_flag = MagicMock()
    manager._stop_flags[42] = fake_flag

    manager.stop_batch(42)

    fake_flag.set.assert_called_once()
    mock_db.batches.update_status.assert_called_once_with(42, BatchStatus.STOPPING)


def test_stop_batch_invalid(mock_db, mock_engine):
    manager = BatchManager(mock_db, engine_manger=mock_engine)
    with pytest.raises(ValueError):
        manager.stop_batch(99)


def test_recover_batches(mock_db, mock_engine):
    manager = BatchManager(mock_db, engine_manger=mock_engine)
    mock_db.batches.list.return_value = [{"id": 10}, {"id": 11}]
    manager.recover_batches()

    # Should update status at least for both "running" and "started"
    assert mock_db.batches.update_status.call_count >= 4


def test_get_engines(mock_db, mock_engine):
    mock_engine.get_engines.return_value = ["test", "gemini", "openai"]
    manager = BatchManager(mock_db, engine_manger=mock_engine)
    assert manager.get_engines() == ["test", "gemini", "openai"]


def test_get_file_readers(mock_db, mock_engine, mock_file_reader):
    manager = BatchManager(mock_db, engine_manger=mock_engine)
    assert manager.get_file_readers() == ["pdf"]
