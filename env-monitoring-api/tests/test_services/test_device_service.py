import pytest
from app.services.room_service import create_room
from app.services.device_service import create_device, list_devices, get_device, set_status, delete_device
from app.models.device import DeviceStatus


def test_create_device(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="Node 1")
    assert device.id is not None
    assert device.room_id == room.id
    assert device.status == DeviceStatus.offline


def test_list_devices(db):
    room = create_room(db, name="R", location="L")
    create_device(db, room_id=room.id, name="N1")
    create_device(db, room_id=room.id, name="N2")
    assert len(list_devices(db)) == 2


def test_get_device(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    found = get_device(db, device.id)
    assert found is not None
    assert found.id == device.id


def test_get_device_not_found(db):
    assert get_device(db, 9999) is None


def test_set_status(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    updated = set_status(db, device.id, DeviceStatus.online)
    assert updated.status == DeviceStatus.online


def test_set_status_not_found(db):
    with pytest.raises(ValueError):
        set_status(db, 9999, DeviceStatus.online)


def test_delete_device(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    assert delete_device(db, device.id) is True
    assert get_device(db, device.id) is None


def test_delete_device_not_found(db):
    assert delete_device(db, 9999) is False
