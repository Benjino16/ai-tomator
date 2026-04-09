import time
from io import BytesIO

import httpx
import pytest

BASE_URL = "http://localhost:8000"


def wait_for_backend(retries=30, delay=1):
    """Waits for the backend to be available at BASE_URL/health."""
    for _ in range(retries):
        try:
            r = httpx.get(f"{BASE_URL}/health")
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(delay)
    raise RuntimeError("Backend not ready")


@pytest.fixture(scope="session", autouse=True)
def ensure_backend_ready():
    """Session fixture that ensures the backend is running."""
    wait_for_backend()


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="session")
def authenticated_client(client):
    """Registers and logs in a test user."""
    r = client.post(
        "/api/authentication/register",
        json={"username": "test", "password": "123456"},
    )
    assert r.status_code == 200 or r.status_code == 400  # User might already exist

    r = client.post(
        "/api/authentication/login",
        json={"username": "test", "password": "123456"},
    )
    assert r.status_code == 200
    return client


def test_health():
    r = httpx.get(f"{BASE_URL}/health")
    assert r.status_code == 200


def test_file_workflow(authenticated_client):
    # Retrieve list of files
    r = authenticated_client.get("/api/files/")
    assert r.status_code == 200

    # Upload a file
    r = authenticated_client.post(
        "/api/files/upload",
        json={"tags": ["test_tag"]},
        files={"file": ("test.txt", BytesIO(b"test"))},
    )
    assert r.status_code == 200
    file_id = r.json()["id"]
    file_name = r.json()["name"]

    # Verify the file is in the list
    r = authenticated_client.get("/api/files/")
    assert r.status_code == 200
    assert file_id in [item["id"] for item in r.json()]
    assert file_name in [item["name"] for item in r.json()]

    # Delete the file
    r = authenticated_client.delete(f"/api/files/delete/{file_id}")
    assert r.status_code == 204


def test_prompt_workflow(authenticated_client):
    # Retrieve prompts
    r = authenticated_client.get("/api/prompts/")
    assert r.status_code == 200

    # Create a prompt
    r = authenticated_client.post(
        "/api/prompts/add",
        json={"name": "test_prompt", "content": "this is a test"},
    )
    assert r.status_code == 200
    result = r.json()
    prompt_id = result["id"]

    # Verify the prompt is in the list
    r = authenticated_client.get("/api/prompts/")
    assert r.status_code == 200
    assert prompt_id in [item["id"] for item in r.json()]

    # Delete the prompt
    r = authenticated_client.delete(f"/api/prompts/delete/{prompt_id}")
    assert r.status_code == 200


def test_batch_workflow(authenticated_client):
    # Create a prompt
    r = authenticated_client.post(
        "/api/prompts/add",
        json={"name": "test_prompt", "content": "this is a test"},
    )
    assert r.status_code == 200
    prompt_id = r.json()["id"]

    # Create an endpoint
    r = authenticated_client.post(
        "/api/endpoints/add",
        json={
            "name": "test_endpoint",
            "client": "test_engine",
            "provider": "self_hosted",
        },
    )
    assert r.status_code == 200
    endpoint_name = r.json()["name"]

    # Upload a file
    r = authenticated_client.post(
        "/api/files/upload",
        json={"tags": ["test_tag"]},
        files={"file": ("test.txt", BytesIO(b"test"))},
    )
    assert r.status_code == 200
    file_id = r.json()["id"]

    # Start a batch
    batch_run_payload = {
        "prompt_id": prompt_id,
        "files": [file_id],
        "endpoint": endpoint_name,
        "file_reader": "pymupdf_default",
        "model": "test_model_pro",
        "delay": 10,
        "temperature": 1.0,
        "json_format": False,
    }
    r = authenticated_client.post("/api/batches/start", json=batch_run_payload)
    assert r.status_code == 200
    batch_id = r.json()["id"]

    # Verify the batch is in the list
    r = authenticated_client.get("/api/batches/")
    assert r.status_code == 200
    assert batch_id in [item["id"] for item in r.json()]
