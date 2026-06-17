from datetime import datetime, timezone
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.services.measurement_service import create_measurement
from app.services.threshold_service import upsert as upsert_threshold
from app.services.user_service import create_user
from app.models.user import UserRole
from app.config import settings

SENSOR_HEADERS = {"Authorization": f"Bearer {settings.sensor_token}"}


def test_room_status_requires_auth(client, db):
    room = create_room(db, name="R", location="L")
    resp = client.get(f"/api/rooms/{room.id}/status")
    assert resp.status_code == 401


def test_room_status_not_found(authed_client, db):
    resp = authed_client.get("/api/rooms/9999/status")
    assert resp.status_code == 404


def test_room_status_unknown_no_device(authed_client, db):
    room = create_room(db, name="Empty Room", location="L")
    resp = authed_client.get(f"/api/rooms/{room.id}/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unknown"


def test_room_status_green(authed_client, db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    upsert_threshold(db, device_id=device.id, temp_min=20.0, temp_max=30.0, humidity_min=40.0, humidity_max=70.0)
    create_measurement(db, device_id=device.id, temperature=25.0, humidity=55.0, timestamp=datetime.now(timezone.utc))
    resp = authed_client.get(f"/api/rooms/{room.id}/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "green"
    assert data["temperature"] == 25.0


def test_list_rooms_requires_auth(client):
    resp = client.get("/api/rooms")
    assert resp.status_code == 401


def test_list_rooms_empty(authed_client):
    resp = authed_client.get("/api/rooms")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_room_requires_admin(client, db):
    create_user(db, username="regular2", password="pass", role=UserRole.user)
    client.post("/login", data={"username": "regular2", "password": "pass"}, follow_redirects=False)
    resp = client.post("/api/rooms", json={"name": "Lab", "location": "Floor 1"})
    assert resp.status_code == 403


def test_create_room(authed_client):
    resp = authed_client.post("/api/rooms", json={"name": "Cold Room", "location": "Basement"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Cold Room"
    assert data["id"] is not None


def test_list_rooms_after_create(authed_client):
    authed_client.post("/api/rooms", json={"name": "R1", "location": "L1"})
    authed_client.post("/api/rooms", json={"name": "R2", "location": "L2"})
    resp = authed_client.get("/api/rooms")
    assert len(resp.json()) == 2
