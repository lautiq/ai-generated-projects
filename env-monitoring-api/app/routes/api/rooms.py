from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user
from app.services import room_service, measurement_service, threshold_service, alert_service, device_service

router = APIRouter(prefix="/api/rooms", tags=["api-rooms"])


@router.get("/{room_id}/status")
def get_room_status(room_id: int, db: Session = Depends(get_db), _=Depends(require_user)):
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    device = device_service.get_by_room(db, room_id)
    if not device:
        return {"room_id": room_id, "status": "unknown", "temperature": None, "humidity": None, "timestamp": None}

    latest = measurement_service.get_latest(db, device.id)
    threshold = threshold_service.get_by_device(db, device.id)
    status = alert_service.compute_status(latest, threshold)

    return {
        "room_id": room_id,
        "device_id": device.id,
        "status": status,
        "temperature": latest.temperature if latest else None,
        "humidity": latest.humidity if latest else None,
        "timestamp": latest.timestamp.isoformat() if latest else None,
    }
