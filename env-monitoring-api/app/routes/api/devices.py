from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user, require_admin
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services import device_service, room_service

router = APIRouter(prefix="/api/devices", tags=["api-devices"])


@router.get("", response_model=list[DeviceResponse])
def list_devices(db: Session = Depends(get_db), _=Depends(require_user)):
    return device_service.list_devices(db)


@router.post("", response_model=DeviceResponse, status_code=201)
def create_device(body: DeviceCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if not room_service.get_room(db, body.room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    return device_service.create_device(db, room_id=body.room_id, name=body.name)
