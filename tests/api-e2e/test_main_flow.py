import pytest
from fastapi.testclient import TestClient
from ai_tomator.app import create_app
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_PDF_PATH_1 = os.path.join(CURRENT_DIR, "..", "fixtures", "sample-1.pdf")
SAMPLE_PDF_PATH_2 = os.path.join(CURRENT_DIR, "..", "fixtures", "sample-2.pdf")


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    tempdir = tmp_path_factory.mktemp("storage")
    test_app = create_app(db_path="sqlite:///:memory:", storage_dir=str(tempdir))

    with TestClient(test_app) as c:
        yield c


@pytest.fixture(scope="session")
def create_endpoint(client):
    endpoint_name = "test_endpoint"
    payload = {
        "name": endpoint_name,
        "engine": "test",
        "url": "endpoint_name",
        "token": "test",
    }
    response = client.post("/api/endpoints/add", json=payload)
    assert response.status_code in (200, 201)
    return response.json()["name"]


@pytest.fixture(scope="session")
def upload_file(client):
    with open(SAMPLE_PDF_PATH_1, "rb") as f:
        resp = client.post(
            "/api/files/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
        )
    assert resp.status_code == 200
    return resp.json()["storage_name"]


def test_main_run(client, create_endpoint, upload_file):
    """
    Testing the api endpoints on a typical main run.
    \n1. Creating an endpoint
    \n2. Upload file
    \n3. Test the api endpoint
    \n4. List Files and check uploaded file
    \n5. Start Batch with the new endpoint and file
    \n6. Stop Batch and check status
    """

    payload = {
        "prompt": "Process dataset",
        "files": [upload_file],
        "endpoint": create_endpoint,
        "file_reader": "pypdf2",
        "model": "gpt-4o",
        "delay": 0,
        "temperature": 0.2,
    }
    response = client.get("/api/batches/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    response = client.post("/api/batches/start", json=payload)
    assert response.status_code in (200, 201)
    batch_response = response.json()
    assert "id" in batch_response
    assert batch_response["prompt"] == "Process dataset"
    assert batch_response["status"] == "starting"


def test_stop_batch(client, create_endpoint, upload_file):
    payload = {
        "prompt": "Process dataset",
        "files": [upload_file, upload_file, upload_file],
        "endpoint": create_endpoint,
        "file_reader": "pypdf2",
        "model": "gpt-4o",
        "delay": 0.01,
        "temperature": 0.2,
    }

    response = client.post("/api/batches/start", json=payload)
    assert response.status_code in (200, 201)
    batch_response = response.json()
    assert "id" in batch_response
    assert batch_response["prompt"] == "Process dataset"
    assert batch_response["status"] == "starting"

    batch_id = batch_response["id"]
    response = client.post("/api/batches/stop", params={"batch_id": batch_id})
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == batch_id
    assert result["status"] in ("stopped", "stopping")

    # todo: currently test TestClient is preventing the worker thread to finish
    # the worker thread therefore never reaches the status "stopped"

    # time.sleep(1)

    # r = client.get(f"/api/batches/{batch_id}")
    # assert r.status_code == 200
    # batch = r.json()
    # status = batch["status"]
    # assert status == "stopped"
