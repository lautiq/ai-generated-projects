from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user, require_admin
from app.models.device import Device
from app.schemas.room import RoomCreate, RoomResponse
from app.services import room_service, measurement_service, threshold_service, alert_service

router = APIRouter(prefix="/api/rooms", tags=["api-rooms"])

@router.get("", response_model=list[RoomResponse])
def list_rooms(db: Session = Depends(get_db), _=Depends(require_user)):
    return room_service.list_rooms(db)

@router.post("", response_model=RoomResponse, status_code=201)
def create_room(body: RoomCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return room_service.create_room(db, name=body.name, location=body.location)

@router.get("/{room_id}/status")
def get_room_status(room_id: int, db: Session = Depends(get_db), _=Depends(require_user)):
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    device = db.query(Device).filter(Device.room_id == room_id).first()
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
