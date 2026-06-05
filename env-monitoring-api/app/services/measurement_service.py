from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.measurement import Measurement
from app.models.device import DeviceStatus
from app.services import device_service


def create_measurement(db: Session, device_id: int, temperature: float, humidity: float, timestamp: datetime) -> Measurement:
    measurement = Measurement(device_id=device_id, temperature=temperature, humidity=humidity, timestamp=timestamp)
    db.add(measurement)
    device_service.set_status(db, device_id, DeviceStatus.online)
    db.commit()
    db.refresh(measurement)
    return measurement


def get_last_24h(db: Session, device_id: int):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    return (
        db.query(Measurement)
        .filter(Measurement.device_id == device_id, Measurement.timestamp >= cutoff)
        .order_by(Measurement.timestamp)
        .all()
    )


def get_latest(db: Session, device_id: int):
    return (
        db.query(Measurement)
        .filter(Measurement.device_id == device_id)
        .order_by(Measurement.timestamp.desc())
        .first()
    )
