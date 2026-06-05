import pytest
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.services.threshold_service import get_by_device, upsert


def _make_device(db):
    room = create_room(db, name="R", location="L")
    return create_device(db, room_id=room.id, name="N")


def test_get_by_device_none(db):
    device = _make_device(db)
    assert get_by_device(db, device.id) is None


def test_upsert_creates(db):
    device = _make_device(db)
    t = upsert(db, device_id=device.id, temp_min=18.0, temp_max=26.0, humidity_min=40.0, humidity_max=70.0)
    assert t.id is not None
    assert t.temp_min == 18.0


def test_upsert_updates(db):
    device = _make_device(db)
    upsert(db, device_id=device.id, temp_min=18.0, temp_max=26.0, humidity_min=40.0, humidity_max=70.0)
    updated = upsert(db, device_id=device.id, temp_min=20.0, temp_max=28.0, humidity_min=45.0, humidity_max=75.0)
    assert updated.temp_min == 20.0
    # Still only one threshold record
    assert get_by_device(db, device.id).temp_max == 28.0


def test_upsert_device_not_found(db):
    with pytest.raises(ValueError, match="Device"):
        upsert(db, device_id=9999, temp_min=18.0, temp_max=26.0, humidity_min=40.0, humidity_max=70.0)


def test_upsert_invalid_temp_range(db):
    device = _make_device(db)
    with pytest.raises(ValueError, match="temp_min"):
        upsert(db, device_id=device.id, temp_min=30.0, temp_max=20.0, humidity_min=40.0, humidity_max=70.0)


def test_upsert_invalid_humidity_range(db):
    device = _make_device(db)
    with pytest.raises(ValueError, match="humidity_min"):
        upsert(db, device_id=device.id, temp_min=18.0, temp_max=26.0, humidity_min=80.0, humidity_max=50.0)


def test_upsert_humidity_out_of_bounds(db):
    device = _make_device(db)
    with pytest.raises(ValueError, match="humidity"):
        upsert(db, device_id=device.id, temp_min=18.0, temp_max=26.0, humidity_min=-5.0, humidity_max=70.0)
