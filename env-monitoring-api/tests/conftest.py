import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import tempfile
import os

from app.db import Base, get_db
from app.main import app
from app.config import settings
# Import all models to register them with Base
from app.models import room, device, measurement, threshold, user

# Use a temporary file for the test database to avoid threading issues
_TEST_DB_FILE = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
_TEST_DB_FILE.close()
SQLITE_URL = f"sqlite:///{_TEST_DB_FILE.name}"

@pytest.fixture
def db():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def authed_client(client, db):
    """Client with an active admin session."""
    from app.services.user_service import create_user
    from app.models.user import UserRole
    create_user(db, username="admin", password="secret", role=UserRole.admin)
    client.post("/login", data={"username": "admin", "password": "secret"}, follow_redirects=False)
    return client
