from fastapi.testclient import TestClient


def test_create(app_client: TestClient):
    payload = {
        "start": "POINT(55.872179 -4.292532)",
        "lost": "POINT(55.873101 -4.290547)",
        "end": "POINT(55.8723 -4.289259)",
        "start_radius": "100",
        "lost_radius": "0",
        "end_radius": "300",
    }
    rv = app_client.post("/position/", json=payload)
    assert rv.status_code == 200, rv.json()
    response = rv.json()
    assert response["id"] is not None
