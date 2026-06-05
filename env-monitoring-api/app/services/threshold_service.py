from sqlalchemy.orm import Session
from app.models.threshold import Threshold


def get_by_device(db: Session, device_id: int):
    return db.query(Threshold).filter(Threshold.device_id == device_id).first()


def upsert(db: Session, device_id: int, temp_min: float, temp_max: float, humidity_min: float, humidity_max: float) -> Threshold:
    from app.models.device import Device

    if not db.query(Device).filter(Device.id == device_id).first():
        raise ValueError(f"Device {device_id} does not exist")
    if temp_min >= temp_max:
        raise ValueError("temp_min must be less than temp_max")
    if not (0 <= humidity_min <= 100) or not (0 <= humidity_max <= 100):
        raise ValueError("humidity values must be between 0 and 100")
    if humidity_min >= humidity_max:
        raise ValueError("humidity_min must be less than humidity_max")

    threshold = get_by_device(db, device_id)
    if threshold:
        threshold.temp_min = temp_min
        threshold.temp_max = temp_max
        threshold.humidity_min = humidity_min
        threshold.humidity_max = humidity_max
    else:
        threshold = Threshold(
            device_id=device_id, temp_min=temp_min, temp_max=temp_max,
            humidity_min=humidity_min, humidity_max=humidity_max,
        )
        db.add(threshold)
    db.commit()
    db.refresh(threshold)
    return threshold
