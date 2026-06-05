from fastapi import Request
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user_service import get_by_username, verify_password


def authenticate_user(db: Session, username: str, password: str):
    user = get_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def login(request: Request, user: User):
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role.value


def logout(request: Request):
    request.session.clear()
