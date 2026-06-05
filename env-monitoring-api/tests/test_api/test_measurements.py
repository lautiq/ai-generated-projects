from datetime import datetime, timezone
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.config import settings

SENSOR_HEADERS = {"Authorization": f"Bearer {settings.sensor_token}"}


def _setup(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    return device


def test_post_measurement_requires_token(client, db):
    device = _setup(db)
    payload = {"temperature": 22.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post(f"/api/devices/{device.id}/measurements", json=payload)
    assert resp.status_code == 401


def test_post_measurement_invalid_token(client, db):
    device = _setup(db)
    payload = {"temperature": 22.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post(f"/api/devices/{device.id}/measurements", json=payload, headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401


def test_post_measurement_success(client, db):
    device = _setup(db)
    payload = {"temperature": 23.5, "humidity": 60.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post(f"/api/devices/{device.id}/measurements", json=payload, headers=SENSOR_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["temperature"] == 23.5
    assert data["device_id"] == device.id


def test_post_measurement_device_not_found(client, db):
    payload = {"temperature": 22.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post("/api/devices/9999/measurements", json=payload, headers=SENSOR_HEADERS)
    assert resp.status_code == 404


def test_get_measurements_requires_auth(client, db):
    device = _setup(db)
    resp = client.get(f"/api/devices/{device.id}/measurements")
    assert resp.status_code == 401


def test_get_measurements_empty(authed_client, db):
    device = _setup(db)
    resp = authed_client.get(f"/api/devices/{device.id}/measurements")
    assert resp.status_code == 200
    assert resp.json() == []
