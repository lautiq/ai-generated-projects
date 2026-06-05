from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.services import device_service, room_service, threshold_service

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")

def _build_items(db):
    devices = device_service.list_devices(db)
    return [
        {
            "device": d,
            "room": room_service.get_room(db, d.room_id),
            "threshold": threshold_service.get_by_device(db, d.id),
        }
        for d in devices
    ]

@router.get("/config", response_class=HTMLResponse)
def config_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)

    message = "Configuración guardada." if request.query_params.get("saved") else None
    return templates.TemplateResponse("config.html", {
        "request": request,
        "devices": _build_items(db),
        "message": message,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })

@router.post("/config/{device_id}", response_class=HTMLResponse)
def save_config(
    device_id: int,
    request: Request,
    temp_min: float = Form(...),
    temp_max: float = Form(...),
    humidity_min: float = Form(...),
    humidity_max: float = Form(...),
    db: Session = Depends(get_db),
):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)

    try:
        threshold_service.upsert(
            db, device_id=device_id,
            temp_min=temp_min, temp_max=temp_max,
            humidity_min=humidity_min, humidity_max=humidity_max,
        )
    except ValueError as e:
        return templates.TemplateResponse("config.html", {
            "request": request,
            "devices": _build_items(db),
            "message": None,
            "error": str(e),
            "username": request.session.get("username"),
            "role": request.session.get("role"),
        }, status_code=422)

    return RedirectResponse("/config?saved=1", status_code=303)
