import pytest
import time
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_PDF_PATH_1 = os.path.join(CURRENT_DIR, "..", "fixtures", "sample-1.pdf")
SAMPLE_PDF_PATH_2 = os.path.join(CURRENT_DIR, "..", "fixtures", "sample-2.pdf")


@pytest.fixture(scope="session")
def create_endpoint(client):
    endpoint_name = "test_endpoint"
    payload = {
        "name": endpoint_name,
        "engine": "test",
        "provider": "self_hosted",
        "url": "endpoint_name",
        "token": "test",
    }
    response = client.post("/api/endpoints/add", json=payload)
    assert response.status_code in (200, 201)
    return response.json()["name"]


@pytest.fixture(scope="session")
def create_prompt(client):
    prompt_name = "test_prompt"
    payload = {
        "name": prompt_name,
        "content": "Process dataset",
    }
    response = client.post("/api/prompts/add", json=payload)
    assert response.status_code in (200, 201)
    return response.json()["id"]


@pytest.fixture(scope="session")
def upload_file(client):
    with open(SAMPLE_PDF_PATH_1, "rb") as f:
        resp = client.post(
            "/api/files/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
        )
    assert resp.status_code == 200
    return resp.json()["storage_name"]


def wait_for_batch_status(client, batch_id, target_status, timeout=10, interval=0.5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = client.get(f"/api/batches/{batch_id}")
        assert response.status_code == 200
        status = response.json()["status"]
        if status == target_status:
            return
        time.sleep(interval)
    assert False, f"Timeout: Batch status is {status}, expected {target_status}"


def test_main_run(client, create_endpoint, upload_file, create_prompt):
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
        "prompt_id": create_prompt,
        "files": [upload_file],
        "endpoint": create_endpoint,
        "file_reader": "pypdf2_default",
        "model": "test_model_fast",
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
    assert batch_response["status"] == "STARTING"


def test_stop_batch(client, create_endpoint, upload_file, create_prompt):
    payload = {
        "prompt_id": create_prompt,
        "files": [upload_file, upload_file, upload_file],
        "endpoint": create_endpoint,
        "file_reader": "pypdf2_default",
        "model": "test_model_fast",
        "delay": 0.01,
        "temperature": 0.2,
    }

    response = client.post("/api/batches/start", json=payload)
    assert response.status_code in (200, 201)
    batch_response = response.json()
    batch_id = batch_response["id"]
    assert batch_response["prompt"] == "Process dataset"
    assert batch_response["status"] == "STARTING"

    response = client.post(f"/api/batches/stop/{batch_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == batch_id
    assert result["status"] in ("STOPPED", "STOPPING")

    wait_for_batch_status(client, batch_id, "STOPPED")
