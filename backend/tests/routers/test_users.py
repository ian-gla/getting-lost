from fastapi.testclient import TestClient
from data.models import Positions, Users


def test_create(app_client: TestClient, create_position: Positions):
    payload = {
        "age": "18-24",
        "gender": "M",
        "nav_skill": 3,
        "position": str(create_position.id),
    }
    rv = app_client.post("/user/", json=payload)
    assert rv.status_code == 200, rv.json()
    response = rv.json()
    assert response["id"] is not None


def test_update(app_client: TestClient, create_user: Users):
    user = create_user
    id = user.id
    payload = {
        "id": id,
        "age": "45-54",
        "gender": "F",
        "nav_skill": 3,
        "position": user.position,
    }
    rv = app_client.put(f"/user/{id}", json=payload)
    assert rv.status_code == 200, rv.json()
    response = rv.json()
    assert response["id"] == id
    assert response["gender"] == "F"
    assert response["position"] == user.position


def test_update_bad_id(app_client: TestClient, create_user: Users):
    user = create_user
    id = -1
    payload = {
        "id": id,
        "age": "45-54",
        "gender": "F",
        "nav_skill": 3,
        "position": user.position,
    }
    rv = app_client.put(f"/user/{id}", json=payload)
    assert rv.status_code == 404, rv.description()
