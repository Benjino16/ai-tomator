import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_tomator.core.engine.models.response_model import EngineResponse
from ai_tomator.manager.database.base import Base
from ai_tomator.manager.database.models.batch import Batch, BatchStatus
from ai_tomator.manager.database.models.file import File
from ai_tomator.manager.database.ops.result_ops import ResultOps

ENGINE_RESPONSE = EngineResponse(
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


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    yield SessionLocal
    engine.dispose()


@pytest.fixture
def result_ops(db_session):
    return ResultOps(db_session)


@pytest.fixture
def sample_data(db_session):
    session = db_session()
    batch = Batch(
        id=1,
        name="test_batch",
        engine="openai",
        endpoint="https://api.openai.com",
        file_reader="txt",
        prompt="say hello",
        model="gpt",
        temperature=0.5,
        status=BatchStatus.COMPLETED,
    )
    file = File(
        id=1,
        storage_name="file1.txt",
        display_name="File 1",
        tags=["tag"],
        mime_type="text/plain",
        size=100,
    )
    session.add_all([batch, file])
    session.commit()
    session.close()


def test_save_and_list(result_ops, sample_data):
    result_ops.save(
        batch_id=1, storage_file_name="file1.txt", engine_response=ENGINE_RESPONSE
    )
    data = result_ops.list_by_batch(1)
    assert len(data) == 1
    r = data[0]
    assert r["storage_file_name"] == "file1.txt"
    assert r["input"] == "input text"
    assert r["output"] == "output text"
    assert r["batch_id"] == 1
    assert r["file_id"] == 1


def test_save_with_invalid_batch(result_ops):
    with pytest.raises(ValueError):
        result_ops.save(
            batch_id=999, storage_file_name="file1.txt", engine_response=ENGINE_RESPONSE
        )


def test_list_by_batch_empty(result_ops, sample_data):
    data = result_ops.list_by_batch(1)
    assert data == []
