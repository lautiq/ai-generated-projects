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


def login(session: dict, user: User):
    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role.value


def logout(session: dict):
    session.clear()
