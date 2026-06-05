from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.services import room_service, device_service, measurement_service, threshold_service, alert_service

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/rooms/{room_id}", response_class=HTMLResponse)
def room_detail(room_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)

    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    device = device_service.get_by_room(db, room_id)
    latest, status = None, "unknown"
    timestamps, temperatures, humidities = [], [], []

    if device:
        latest = measurement_service.get_latest(db, device.id)
        threshold = threshold_service.get_by_device(db, device.id)
        status = alert_service.compute_status(latest, threshold)
        history = measurement_service.get_last_24h(db, device.id)
        timestamps = [m.timestamp.strftime("%H:%M") for m in history]
        temperatures = [m.temperature for m in history]
        humidities = [m.humidity for m in history]

    return templates.TemplateResponse("room_detail.html", {
        "request": request,
        "room": room,
        "latest": latest,
        "status": status,
        "timestamps": timestamps,
        "temperatures": temperatures,
        "humidities": humidities,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })
