from datetime import datetime, timedelta, timezone
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.services.measurement_service import create_measurement, get_last_24h, get_latest
from app.models.device import DeviceStatus


def _make_device(db):
    room = create_room(db, name="R", location="L")
    return create_device(db, room_id=room.id, name="N")


def test_create_measurement(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    m = create_measurement(db, device_id=device.id, temperature=22.5, humidity=55.0, timestamp=now)
    assert m.id is not None
    assert m.temperature == 22.5


def test_create_measurement_sets_device_online(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=22.5, humidity=55.0, timestamp=now)
    db.refresh(device)
    assert device.status == DeviceStatus.online


def test_get_last_24h_returns_recent(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=20.0, humidity=50.0, timestamp=now - timedelta(hours=1))
    create_measurement(db, device_id=device.id, temperature=21.0, humidity=51.0, timestamp=now - timedelta(hours=23))
    results = get_last_24h(db, device.id)
    assert len(results) == 2


def test_get_last_24h_excludes_old(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=20.0, humidity=50.0, timestamp=now - timedelta(hours=25))
    results = get_last_24h(db, device.id)
    assert len(results) == 0


def test_get_latest(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=20.0, humidity=50.0, timestamp=now - timedelta(hours=2))
    create_measurement(db, device_id=device.id, temperature=25.0, humidity=60.0, timestamp=now)
    latest = get_latest(db, device.id)
    assert latest.temperature == 25.0


def test_get_latest_no_measurements(db):
    device = _make_device(db)
    assert get_latest(db, device.id) is None
