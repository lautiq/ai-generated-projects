from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user, verify_sensor_token
from app.schemas.measurement import MeasurementCreate, MeasurementResponse
from app.services import measurement_service, device_service

router = APIRouter(prefix="/api/devices", tags=["api-measurements"])


@router.post("/{device_id}/measurements", response_model=MeasurementResponse, status_code=201)
def create_measurement(
    device_id: int,
    body: MeasurementCreate,
    db: Session = Depends(get_db),
    _=Depends(verify_sensor_token),
):
    if not device_service.get_device(db, device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    return measurement_service.create_measurement(
        db, device_id=device_id, temperature=body.temperature,
        humidity=body.humidity, timestamp=body.timestamp,
    )


@router.get("/{device_id}/measurements", response_model=list[MeasurementResponse])
def get_measurements(
    device_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    if not device_service.get_device(db, device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    return measurement_service.get_last_24h(db, device_id)
