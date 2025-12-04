import pytest
from fastapi.testclient import TestClient
from ai_tomator.app import create_app


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    tempdir = tmp_path_factory.mktemp("storage")
    test_app = create_app(db_path="sqlite:///:memory:", storage_dir=str(tempdir))

    with TestClient(test_app) as c:
        yield c
