import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ai_tomator.manager.database.base import Base
from ai_tomator.manager.database.models.file import File
from ai_tomator.manager.database.ops.file_ops import FileOps


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    yield SessionLocal
    engine.dispose()


@pytest.fixture
def file_ops(db_session):
    return FileOps(db_session)


def test_add_and_get_file(file_ops):
    file_ops.add("f1.txt", "MyFile", ["tag1", "tag2"], "text/plain", 123)
    data = file_ops.get("f1.txt")
    assert data["display_name"] == "MyFile"
    assert data["storage_name"] == "f1.txt"
    assert data["tags"] == ["tag1", "tag2"]
    assert data["mime_type"] == "text/plain"
    assert data["size"] == 123


def test_get_not_found(file_ops):
    with pytest.raises(ValueError):
        file_ops.get("missing.txt")


def test_list_and_delete(file_ops):
    file_ops.add("a.txt", "A", [], "text/plain", 10)
    file_ops.add("b.txt", "B", [], "text/plain", 20)
    listed = file_ops.list()
    assert len(listed) == 2
    file_ops.delete("a.txt")
    listed_after = file_ops.list()
    assert len(listed_after) == 1
    assert listed_after[0]["storage_name"] == "b.txt"


def test_delete_not_found(file_ops):
    with pytest.raises(ValueError):
        file_ops.delete("unknown.txt")
