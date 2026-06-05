from app.services.user_service import create_user, get_by_username, list_users, delete_user, verify_password
from app.models.user import UserRole


def test_create_user(db):
    user = create_user(db, username="alice", password="pass123", role=UserRole.user)
    assert user.id is not None
    assert user.username == "alice"
    assert user.password_hash != "pass123"


def test_get_by_username(db):
    create_user(db, username="bob", password="pass", role=UserRole.user)
    found = get_by_username(db, "bob")
    assert found is not None
    assert found.username == "bob"


def test_get_by_username_not_found(db):
    assert get_by_username(db, "nobody") is None


def test_list_users(db):
    create_user(db, username="u1", password="p", role=UserRole.user)
    create_user(db, username="u2", password="p", role=UserRole.admin)
    assert len(list_users(db)) == 2


def test_delete_user(db):
    user = create_user(db, username="del_me", password="p", role=UserRole.user)
    assert delete_user(db, user.id) is True
    assert get_by_username(db, "del_me") is None


def test_delete_user_not_found(db):
    assert delete_user(db, 9999) is False


def test_verify_password(db):
    user = create_user(db, username="pw_test", password="correct", role=UserRole.user)
    assert verify_password("correct", user.password_hash) is True
    assert verify_password("wrong", user.password_hash) is False
