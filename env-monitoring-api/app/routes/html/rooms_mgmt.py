from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.services import room_service

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/rooms", response_class=HTMLResponse)
def rooms_list(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("rooms.html", {
        "request": request,
        "rooms": room_service.list_rooms(db),
        "message": "Habitación creada." if request.query_params.get("created") else None,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })

@router.post("/rooms")
def create_room(
    request: Request,
    name: str = Form(...),
    location: str = Form(...),
    db: Session = Depends(get_db),
):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)
    if request.session.get("role") != "admin":
        return RedirectResponse("/rooms", status_code=303)
    room_service.create_room(db, name=name, location=location)
    return RedirectResponse("/rooms?created=1", status_code=303)
