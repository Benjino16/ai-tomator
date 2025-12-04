def test_prompt_api(client):
    # test prompt list api route / empty list
    response = client.get("/api/prompts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    payload = {
        "name": "test_prompt",
        "prompt": "Process dataset",
    }

    # test adding a prompt
    response = client.post("/api/prompts/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    prompt_id_1 = data["id"]
    assert data["name"] == "test_prompt"
    assert data["prompt"] == "Process dataset"

    # add prompt with the same name / should not be possible
    response = client.post("/api/prompts/add", json=payload)
    assert response.status_code == 409

    payload = {
        "name": "test_prompt2",
        "prompt": "Process dataset",
    }

    # add another prompt
    response = client.post("/api/prompts/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    prompt_id_2 = data["id"]

    # check if both prompts exits
    response = client.get("/api/prompts/")
    assert response.status_code == 200
    data = response.json()
    assert any(d["id"] == prompt_id_1 for d in data)
    assert any(d["id"] == prompt_id_2 for d in data)

    # delete first prompt
    response = client.delete(f"/api/prompts/delete/{prompt_id_1}")
    assert response.status_code == 200
    data = response.json()
    assert prompt_id_1 == data["id"]

    # check if the first prompt was deleted successfully
    response = client.get("/api/prompts/")
    assert response.status_code == 200
    data = response.json()
    assert not any(d["id"] == prompt_id_1 for d in data)
