import pytest
from fastapi.testclient import TestClient
from ai_tomator.app import create_app


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    tempdir = tmp_path_factory.mktemp("storage")
    db_file = tmp_path_factory.mktemp("db") / "test.db"
    test_app = create_app(db_path=f"sqlite:///{db_file}", storage_dir=str(tempdir))

    with TestClient(test_app) as c:
        yield c
