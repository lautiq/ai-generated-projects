from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.user import UserRole
from app.services import user_service

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")

def _require_admin(request: Request, db: Session):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=303)
    return None

@router.get("/users", response_class=HTMLResponse)
def users_page(request: Request, db: Session = Depends(get_db)):
    redirect = _require_admin(request, db)
    if redirect:
        return redirect

    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": user_service.list_users(db),
        "current_user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "role": request.session.get("role"),
        "error": None,
    })

@router.post("/users")
def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
):
    redirect = _require_admin(request, db)
    if redirect:
        return redirect

    if user_service.get_by_username(db, username):
        return templates.TemplateResponse("users.html", {
            "request": request,
            "users": user_service.list_users(db),
            "current_user_id": request.session.get("user_id"),
            "username": request.session.get("username"),
            "role": request.session.get("role"),
            "error": f"El usuario '{username}' ya existe.",
        }, status_code=400)

    user_service.create_user(db, username=username, password=password, role=UserRole(role))
    return RedirectResponse("/users", status_code=303)

@router.post("/users/{user_id}/delete")
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = _require_admin(request, db)
    if redirect:
        return redirect
    user_service.delete_user(db, user_id)
    return RedirectResponse("/users", status_code=303)
