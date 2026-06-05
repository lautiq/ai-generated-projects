from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.device import Device
from app.services import room_service, measurement_service, threshold_service, alert_service

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)

    rooms = room_service.list_rooms(db)
    rooms_data = []
    for room in rooms:
        device = db.query(Device).filter(Device.room_id == room.id).first()
        latest = measurement_service.get_latest(db, device.id) if device else None
        threshold = threshold_service.get_by_device(db, device.id) if device else None
        status = alert_service.compute_status(latest, threshold)
        rooms_data.append({"room": room, "device": device, "latest": latest, "status": status})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "rooms": rooms_data,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })
