from sqlalchemy.orm import Session
from app.models.device import Device, DeviceStatus


def create_device(db: Session, room_id: int, name: str) -> Device:
    device = Device(room_id=room_id, name=name)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def list_devices(db: Session):
    return db.query(Device).all()


def get_device(db: Session, device_id: int):
    return db.query(Device).filter(Device.id == device_id).first()


def get_by_room(db: Session, room_id: int):
    return db.query(Device).filter(Device.room_id == room_id).first()


def set_status(db: Session, device_id: int, status: DeviceStatus) -> Device:
    device = get_device(db, device_id)
    if not device:
        raise ValueError(f"Device {device_id} not found")
    device.status = status
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> bool:
    device = get_device(db, device_id)
    if not device:
        return False
    db.delete(device)
    db.commit()
    return True
