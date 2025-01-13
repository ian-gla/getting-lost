from fastapi.testclient import TestClient
from data.models import Positions


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
