import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from ai_tomator.manager.database.base import Base
from ai_tomator.manager.database.models.endpoint import Endpoint
from ai_tomator.manager.database.ops.endpoint_ops import EndpointOps
from ai_tomator.core.exceptions import NameAlreadyExistsError


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    yield SessionLocal
    engine.dispose()


@pytest.fixture
def endpoint_ops(db_session):
    return EndpointOps(db_session)


def test_add_and_get_endpoint(endpoint_ops):
    endpoint_ops.add("openai", "openai", "https://api.openai.com", "tokentest")
    data = endpoint_ops.get("openai", show_api=True)
    assert data["name"] == "openai"
    assert data["engine"] == "openai"
    assert data["url"] == "https://api.openai.com"
    assert data["token"] == "tokentest"


def test_add_duplicate_raises(endpoint_ops):
    endpoint_ops.add("openai", "openai")
    with pytest.raises(NameAlreadyExistsError):
        endpoint_ops.add("openai", "openai")


def test_get_not_found(endpoint_ops):
    with pytest.raises(ValueError):
        endpoint_ops.get("missing")


def test_list_and_delete(endpoint_ops):
    endpoint_ops.add("one", "engine1")
    endpoint_ops.add("two", "engine2")
    listed = endpoint_ops.list()
    assert len(listed) == 2
    endpoint_ops.delete("one")
    listed_after = endpoint_ops.list()
    assert len(listed_after) == 1
    assert listed_after[0]["name"] == "two"


def test_delete_not_found(endpoint_ops):
    with pytest.raises(ValueError):
        endpoint_ops.delete("missing")
