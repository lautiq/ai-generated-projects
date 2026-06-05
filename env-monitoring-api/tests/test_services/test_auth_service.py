from app.services.user_service import create_user
from app.services.auth_service import authenticate_user
from app.models.user import UserRole


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
