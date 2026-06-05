from unittest.mock import MagicMock
from app.services.user_service import create_user
from app.services.auth_service import authenticate_user, login, logout
from app.models.user import UserRole, User


def test_authenticate_valid(db):
    create_user(db, username="auth_user", password="secret", role=UserRole.user)
    user = authenticate_user(db, "auth_user", "secret")
    assert user is not None
    assert user.username == "auth_user"


def test_authenticate_wrong_password(db):
    create_user(db, username="auth_user2", password="secret", role=UserRole.user)
    assert authenticate_user(db, "auth_user2", "wrong") is None


def test_authenticate_unknown_user(db):
    assert authenticate_user(db, "ghost", "secret") is None


def test_login_sets_session(db):
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "login_user"
    user.role = UserRole.admin
    session = {}
    login(session, user)
    assert session["user_id"] == 1
    assert session["username"] == "login_user"
    assert session["role"] == "admin"


def test_logout_clears_session(db):
    session = {"user_id": 1, "username": "x", "role": "user"}
    logout(session)
    assert session == {}
