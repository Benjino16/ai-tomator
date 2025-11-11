import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ai_tomator.manager.database.base import Base
from ai_tomator.manager.database.models.batch import BatchFile
from ai_tomator.manager.database.models.file import File
from ai_tomator.manager.database.ops.batch_ops import BatchOps


@pytest.fixture
def session_local():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    yield SessionLocal
    engine.dispose()


@pytest.fixture
def setup_data(session_local):
    session = session_local()
    file1 = File(
        display_name="file1.txt",
        storage_name="f1",
        tags=[],
        mime_type="text/plain",
        size=10,
    )
    file2 = File(
        display_name="file2.txt",
        storage_name="f2",
        tags=[],
        mime_type="text/plain",
        size=20,
    )
    session.add_all([file1, file2])
    session.commit()
    session.close()
    return session_local


def test_add_and_get_batch(setup_data):
    ops = BatchOps(setup_data)
    batch = ops.add(
        "b1",
        "created",
        ["f1", "f2"],
        "engine",
        "endpoint",
        "reader",
        "prompt",
        "model",
        0.5,
    )
    fetched = ops.get(batch["id"])
    assert fetched["name"] == "b1"
    assert fetched["status"] == "created"


def test_add_missing_file_raises(setup_data):
    ops = BatchOps(setup_data)
    with pytest.raises(ValueError):
        ops.add("b1", "created", ["missing"], "e", "e", "r", "p", "m", 0.5)


def test_update_status(setup_data):
    ops = BatchOps(setup_data)
    batch = ops.add("b1", "created", ["f1"], "e", "e", "r", "p", "m", 0.5)
    updated = ops.update_status(batch["id"], "done")
    assert updated["status"] == "done"


def test_update_batch_file_status(setup_data):
    ops = BatchOps(setup_data)
    batch = ops.add("b1", "created", ["f1"], "e", "e", "r", "p", "m", 0.5)
    ops.update_batch_file_status(batch["id"], "f1", "processed")
    with setup_data() as s:
        bf = (
            s.query(BatchFile)
            .filter_by(batch_id=batch["id"], storage_name="f1")
            .first()
        )
        assert bf.status == "processed"


def test_list_batches(setup_data):
    ops = BatchOps(setup_data)
    ops.add("b1", "created", ["f1"], "e", "e", "r", "p", "m", 0.5)
    ops.add("b2", "done", ["f2"], "e", "e", "r", "p", "m", 0.5)
    all_batches = ops.list()
    done_batches = ops.list("done")
    assert len(all_batches) == 2
    assert len(done_batches) == 1
