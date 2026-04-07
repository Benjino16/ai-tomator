import os
from io import BytesIO

import httpx
import time
import pytest
from testcontainers.compose import DockerCompose

BASE_URL = "http://localhost:8000"

os.environ['COMPOSE_PROJECT_NAME'] = 'ai_tomator_test'

@pytest.fixture(scope="session")
def compose():
    with DockerCompose(
        ".",
        compose_file_name=["compose.yaml", "compose.build.yaml"],
    ) as compose:
        wait_for_backend()
        yield compose

def wait_for_backend():
    for _ in range(30):
        try:
            r = httpx.get("http://localhost:8000/health")
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Backend not ready")

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

@pytest.fixture(scope="session")
def authenticated_client(client):
    r = client.post(
        "/api/authentication/register",
        json={"username": "test", "password": "123456"},
    )
    assert r.status_code == 200
    r = client.post(
        "/api/authentication/login",
        json={"username": "test", "password": "123456"},
    )
    assert r.status_code == 200
    return client


def test_health(compose):
    r = httpx.get(f"{BASE_URL}/health")
    assert r.status_code == 200

def test_file_workflow(compose, authenticated_client):
    r = authenticated_client.get(f"{BASE_URL}/api/files/")
    assert r.status_code == 200

    r = authenticated_client.post(f"{BASE_URL}/api/files/upload", json={"tags": ["test_tag"]}, files={"file": BytesIO(b"test"), "filename": "test.txt"})
    assert r.status_code == 200
    file_id = r.json()["id"]
    file_name = r.json()["name"]
    r = authenticated_client.get(f"{BASE_URL}/api/files/")
    assert r.status_code == 200
    assert file_id in [item['id'] for item in r.json()]
    assert file_name in [item['name'] for item in r.json()]

    r = authenticated_client.delete(f"{BASE_URL}/api/files/delete/{file_id}")
    assert r.status_code == 204

def test_prompt_workflow(compose, authenticated_client):
    r = authenticated_client.get(f"{BASE_URL}/api/prompts/")
    assert r.status_code == 200

    r = authenticated_client.post(f"{BASE_URL}/api/prompts/add", json={"name": "test_prompt", "content": "this is a test"})
    assert r.status_code == 200
    result = r.json()
    prompt_id = result["id"]
    prompt_name = result["name"]
    prompt_content = result["content"]
    r = authenticated_client.get(f"{BASE_URL}/api/prompts/")
    assert r.status_code == 200
    assert prompt_id in [item['id'] for item in r.json()]
    assert prompt_name in [item['name'] for item in r.json()]
    assert prompt_content in [item['content'] for item in r.json()]

    r = authenticated_client.delete(f"{BASE_URL}/api/prompts/delete/{prompt_id}")
    assert r.status_code == 200

def test_batch_workflow(compose, authenticated_client):
    r = authenticated_client.get(f"{BASE_URL}/api/batches/")
    assert r.status_code == 200

    r = authenticated_client.post(f"{BASE_URL}/api/prompts/add",
                                  json={"name": "test_prompt", "content": "this is a test"})
    assert r.status_code == 200
    prompt_id = r.json()["id"]

    r = authenticated_client.post(f"{BASE_URL}/api/endpoints/add",
                                  json={"name": "test_endpoint", "client": "test_engine", "provider": "self_hosted"})
    assert r.status_code == 200
    endpoint_name = r.json()["name"]

    r = authenticated_client.post(f"{BASE_URL}/api/files/upload", json={"tags": ["test_tag"]},
                                  files={"file": BytesIO(b"test"), "filename": "test.txt"})
    assert r.status_code == 200
    file_id = r.json()["id"]

    batch_run_payload = {
        "prompt_id": prompt_id,
        "files": [file_id],
        "endpoint": endpoint_name,
        "file_reader": "pymupdf_default",
        "model": "test_model_pro",
        "delay": 10,
        "temperature": 1.0,
        "json_format": False
    }
    r = authenticated_client.post(f"{BASE_URL}/api/batches/start", json=batch_run_payload)
    assert r.status_code == 200
    batch_id = r.json()["id"]

    r = authenticated_client.get(f"{BASE_URL}/api/batches/")
    assert r.status_code == 200
    assert batch_id in [item['id'] for item in r.json()]
