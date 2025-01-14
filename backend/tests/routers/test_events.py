from fastapi.testclient import TestClient
from data.models import Positions, Users, Events


def test_create(app_client: TestClient, create_position: Positions, create_user: Users):
    payload = {
        "user": str(create_user.id),
        "position": str(create_position.id),
        "when": "This week",
        "time_of_day": "Morning",
        "day_of_week": "Monday",
        "guidance": "Smart Phone/Sat Nav",
        "group": "No",
        "factors": "Environment",
        "familiarity": "1",
        "context": "",
        "explain": "",
    }
    rv = app_client.post("/event/", json=payload)
    assert rv.status_code == 200, rv.json()
    response = rv.json()
    assert response["id"] is not None


def test_update(app_client: TestClient, create_event: Events):
    event = create_event
    payload = {
        "user": str(event.user),
        "position": str(event.position),
        "when": "This week",
        "time_of_day": "Morning",
        "day_of_week": "Monday",
        "guidance": "Smart Phone/Sat Nav",
        "group": "Yes",
        "factors": "Environment",
        "familiarity": "3",
        "context": "This is some context",
        "explain": "And here is some explaination",
    }
    rv = app_client.put(f"/event/{event.id}", json=payload)
    assert rv.status_code == 200, rv.json()
    response = rv.json()
    assert response["id"] is not None
    assert response["id"] == event.id
    assert response["user"] == event.user
    assert response["position"] == event.position
    assert response["when"] == "This week"
    assert response["group"] == "Yes"
    assert response["context"] == "This is some context"
    assert response["explain"] == "And here is some explaination"


def test_update_bad_id(app_client: TestClient, create_event: Events):
    event = create_event
    payload = {
        "user": str(event.user),
        "position": str(event.position),
        "when": "This week",
        "time_of_day": "Morning",
        "day_of_week": "Monday",
        "guidance": "Smart Phone/Sat Nav",
        "group": "Yes",
        "factors": "Environment",
        "familiarity": "3",
        "context": "This is some context",
        "explain": "And here is some explaination",
    }
    id = -1
    rv = app_client.put(f"/event/{id}", json=payload)
    assert rv.status_code == 404, rv.json()
