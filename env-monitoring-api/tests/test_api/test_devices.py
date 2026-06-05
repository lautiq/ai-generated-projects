from app.services.room_service import create_room
from app.services.user_service import create_user
from app.models.user import UserRole


def test_list_devices_requires_auth(client):
    resp = client.get("/api/devices")
    assert resp.status_code == 401


def test_list_devices_empty(authed_client, db):
    resp = authed_client.get("/api/devices")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_device_requires_admin(client, db):
    room = create_room(db, name="R", location="L")
    create_user(db, username="regular", password="pass", role=UserRole.user)
    client.post("/login", data={"username": "regular", "password": "pass"}, follow_redirects=False)
    resp = client.post("/api/devices", json={"room_id": room.id, "name": "Node"})
    assert resp.status_code == 403


def test_create_device(authed_client, db):
    room = create_room(db, name="Lab", location="Floor 1")
    resp = authed_client.post("/api/devices", json={"room_id": room.id, "name": "Node 1"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Node 1"
    assert data["room_id"] == room.id
    assert data["status"] == "offline"


def test_create_device_room_not_found(authed_client, db):
    resp = authed_client.post("/api/devices", json={"room_id": 9999, "name": "Ghost Node"})
    assert resp.status_code == 404


def test_list_devices_after_create(authed_client, db):
    room = create_room(db, name="R", location="L")
    authed_client.post("/api/devices", json={"room_id": room.id, "name": "N1"})
    authed_client.post("/api/devices", json={"room_id": room.id, "name": "N2"})
    resp = authed_client.get("/api/devices")
    assert len(resp.json()) == 2
