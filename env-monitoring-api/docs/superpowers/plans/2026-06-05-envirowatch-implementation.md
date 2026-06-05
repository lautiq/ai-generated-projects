# EnviroWatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI web application for IoT environmental monitoring with device/room management, sensor data ingestion via REST, alert visualization, and user management.

**Architecture:** FastAPI serves Jinja2 HTML pages for the web UI and JSON API endpoints for sensor nodes and AJAX data fetching. A service layer mediates between routes and SQLAlchemy ORM. Auth uses signed cookie sessions for web users and a static Bearer token for IoT sensor nodes.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy (sync), Alembic, PostgreSQL, Jinja2, Bootstrap 5 (CDN), Chart.js (CDN), passlib[bcrypt], pydantic-settings, pytest, httpx

---

## File Map

| File | Responsibility |
|---|---|
| `requirements.txt` | All Python dependencies |
| `.env.example` | Required environment variable template |
| `app/config.py` | Settings loaded from env vars via pydantic-settings |
| `app/db.py` | SQLAlchemy engine, SessionLocal, Base, get_db |
| `app/main.py` | FastAPI app instance, middleware, router registration |
| `app/dependencies.py` | get_db, get_session_user, require_user, require_admin, verify_sensor_token |
| `app/models/room.py` | Room ORM model |
| `app/models/device.py` | Device ORM model + DeviceStatus enum |
| `app/models/measurement.py` | Measurement ORM model |
| `app/models/threshold.py` | Threshold ORM model |
| `app/models/user.py` | User ORM model + UserRole enum |
| `app/schemas/room.py` | RoomCreate, RoomResponse |
| `app/schemas/device.py` | DeviceCreate, DeviceResponse |
| `app/schemas/measurement.py` | MeasurementCreate, MeasurementResponse |
| `app/schemas/threshold.py` | ThresholdUpsert, ThresholdResponse |
| `app/schemas/user.py` | UserCreate, UserResponse |
| `app/services/user_service.py` | create_user, get_by_username, list_users, delete_user, hash_password, verify_password |
| `app/services/auth_service.py` | authenticate_user, login, logout |
| `app/services/room_service.py` | create_room, list_rooms, get_room |
| `app/services/device_service.py` | create_device, list_devices, get_device, set_status, delete_device |
| `app/services/measurement_service.py` | create_measurement, get_last_24h, get_latest |
| `app/services/threshold_service.py` | get_by_device, upsert |
| `app/services/alert_service.py` | compute_status → "green"/"yellow"/"red"/"unknown" |
| `app/routes/html/auth.py` | GET /login, POST /login, POST /logout |
| `app/routes/html/dashboard.py` | GET / |
| `app/routes/html/rooms.py` | GET /rooms/{id} |
| `app/routes/html/config.py` | GET /config, POST /config/{device_id} |
| `app/routes/html/users.py` | GET /users, POST /users, DELETE /users/{id} |
| `app/routes/api/devices.py` | GET /api/devices, POST /api/devices |
| `app/routes/api/measurements.py` | POST /api/devices/{id}/measurements, GET /api/devices/{id}/measurements |
| `app/routes/api/rooms.py` | GET /api/rooms/{id}/status |
| `app/templates/base.html` | Bootstrap 5 navbar, block content, block scripts |
| `app/templates/login.html` | Login form |
| `app/templates/dashboard.html` | Rooms grid with status color cards |
| `app/templates/room_detail.html` | Current values + Chart.js 24h graph |
| `app/templates/config.html` | Threshold form per device |
| `app/templates/users.html` | User list + create form (admin only) |
| `app/static/css/custom.css` | Minimal custom styles |
| `tests/conftest.py` | SQLite in-memory db fixture, TestClient fixture |
| `tests/test_services/test_user_service.py` | Unit tests for user_service |
| `tests/test_services/test_auth_service.py` | Unit tests for auth_service |
| `tests/test_services/test_room_service.py` | Unit tests for room_service |
| `tests/test_services/test_device_service.py` | Unit tests for device_service |
| `tests/test_services/test_measurement_service.py` | Unit tests for measurement_service |
| `tests/test_services/test_threshold_service.py` | Unit tests for threshold_service |
| `tests/test_services/test_alert_service.py` | Unit tests for alert_service |
| `tests/test_api/test_devices.py` | Integration tests for /api/devices |
| `tests/test_api/test_measurements.py` | Integration tests for /api/devices/{id}/measurements |
| `tests/test_api/test_rooms_api.py` | Integration tests for /api/rooms/{id}/status |

---

## Task 1: Project Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `app/db.py`
- Create: `app/main.py`
- Create: `app/static/css/custom.css`

- [ ] **Step 1: Create requirements.txt**

```
fastapi[all]==0.115.6
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
alembic==1.14.0
passlib[bcrypt]==1.7.4
pydantic-settings==2.7.0
python-dotenv==1.0.1
pytest==8.3.4
httpx==0.28.1
```

- [ ] **Step 2: Create .env.example**

```
DATABASE_URL=postgresql://user:password@localhost:5432/envirowatch
SECRET_KEY=change-this-to-a-random-secret
SENSOR_TOKEN=change-this-to-a-random-token
```

- [ ] **Step 3: Create app/config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    sensor_token: str

    model_config = {"env_file": ".env"}

settings = Settings()
```

- [ ] **Step 4: Create app/db.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Create app/main.py**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings

app = FastAPI(title="EnviroWatch")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
```

- [ ] **Step 6: Create app/static/css/custom.css**

```css
.card { transition: box-shadow 0.2s; }
.card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.15); }
```

- [ ] **Step 7: Create empty __init__.py files**

```
app/__init__.py          (empty)
app/models/__init__.py   (empty)
app/schemas/__init__.py  (empty)
app/services/__init__.py (empty)
app/routes/__init__.py   (empty)
app/routes/html/__init__.py (empty)
app/routes/api/__init__.py  (empty)
tests/__init__.py           (empty)
tests/test_services/__init__.py (empty)
tests/test_api/__init__.py      (empty)
```

- [ ] **Step 8: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 9: Commit**

```bash
git add requirements.txt .env.example app/
git commit -m "feat: project bootstrap — config, db, main"
```

---

## Task 2: SQLAlchemy Models

**Files:**
- Create: `app/models/room.py`
- Create: `app/models/device.py`
- Create: `app/models/measurement.py`
- Create: `app/models/threshold.py`
- Create: `app/models/user.py`

Note: all `Enum` columns use `native_enum=False` so SQLite works in tests.

- [ ] **Step 1: Create app/models/room.py**

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

- [ ] **Step 2: Create app/models/device.py**

```python
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base

class DeviceStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    maintenance = "maintenance"

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(Enum(DeviceStatus, native_enum=False), nullable=False, default=DeviceStatus.offline)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    room = relationship("Room")
    measurements = relationship("Measurement", back_populates="device", cascade="all, delete-orphan")
    threshold = relationship("Threshold", back_populates="device", uselist=False, cascade="all, delete-orphan")
```

- [ ] **Step 3: Create app/models/measurement.py**

```python
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    device = relationship("Device", back_populates="measurements")
```

- [ ] **Step 4: Create app/models/threshold.py**

```python
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, unique=True)
    temp_min = Column(Float, nullable=False)
    temp_max = Column(Float, nullable=False)
    humidity_min = Column(Float, nullable=False)
    humidity_max = Column(Float, nullable=False)

    device = relationship("Device", back_populates="threshold")
```

- [ ] **Step 5: Create app/models/user.py**

```python
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, func
from app.db import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), nullable=False, default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

- [ ] **Step 6: Commit**

```bash
git add app/models/
git commit -m "feat: SQLAlchemy ORM models"
```

---

## Task 3: Alembic Setup + Initial Migration

**Files:**
- Create: `alembic.ini`
- Modify: `alembic/env.py`
- Create: `alembic/versions/001_initial_schema.py` (auto-generated)

- [ ] **Step 1: Initialize Alembic**

```bash
alembic init alembic
```

- [ ] **Step 2: Update alembic/env.py**

Replace the `target_metadata` section and add the import block so Alembic can detect models:

```python
# At the top of alembic/env.py, after existing imports:
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import Base
from app.models import room, device, measurement, threshold, user  # noqa: F401
from app.config import settings

# Replace the config.set_main_option line:
config.set_main_option("sqlalchemy.url", settings.database_url)

# Replace target_metadata line:
target_metadata = Base.metadata
```

- [ ] **Step 3: Create .env file (not committed) from .env.example and point to a local PostgreSQL database**

Make sure PostgreSQL is running and the database exists:
```bash
createdb envirowatch
```

- [ ] **Step 4: Generate initial migration**

```bash
alembic revision --autogenerate -m "initial schema"
```

Expected: creates `alembic/versions/<hash>_initial_schema.py` with `op.create_table` calls for all 5 tables.

- [ ] **Step 5: Apply migration**

```bash
alembic upgrade head
```

Expected output: no errors, tables created in the database.

- [ ] **Step 6: Commit**

```bash
git add alembic/
git commit -m "feat: Alembic setup and initial schema migration"
```

---

## Task 4: Pydantic Schemas + Dependencies

**Files:**
- Create: `app/schemas/room.py`
- Create: `app/schemas/device.py`
- Create: `app/schemas/measurement.py`
- Create: `app/schemas/threshold.py`
- Create: `app/schemas/user.py`
- Create: `app/dependencies.py`

- [ ] **Step 1: Create app/schemas/room.py**

```python
from pydantic import BaseModel
from datetime import datetime

class RoomCreate(BaseModel):
    name: str
    location: str

class RoomResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Create app/schemas/device.py**

```python
from pydantic import BaseModel
from datetime import datetime
from app.models.device import DeviceStatus

class DeviceCreate(BaseModel):
    room_id: int
    name: str

class DeviceResponse(BaseModel):
    id: int
    room_id: int
    name: str
    status: DeviceStatus
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Create app/schemas/measurement.py**

```python
from pydantic import BaseModel, Field
from datetime import datetime

class MeasurementCreate(BaseModel):
    temperature: float
    humidity: float = Field(ge=0, le=100)
    timestamp: datetime

class MeasurementResponse(BaseModel):
    id: int
    device_id: int
    temperature: float
    humidity: float
    timestamp: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Create app/schemas/threshold.py**

```python
from pydantic import BaseModel

class ThresholdUpsert(BaseModel):
    temp_min: float
    temp_max: float
    humidity_min: float
    humidity_max: float

class ThresholdResponse(BaseModel):
    id: int
    device_id: int
    temp_min: float
    temp_max: float
    humidity_min: float
    humidity_max: float

    model_config = {"from_attributes": True}
```

- [ ] **Step 5: Create app/schemas/user.py**

```python
from pydantic import BaseModel
from datetime import datetime
from app.models.user import UserRole

class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.user

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 6: Create app/dependencies.py**

```python
from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, UserRole
from app.config import settings

def get_session_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_session_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_admin(user: User = Depends(require_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user

def verify_sensor_token(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth[7:]
    if token != settings.sensor_token:
        raise HTTPException(status_code=401, detail="Invalid sensor token")
```

- [ ] **Step 7: Commit**

```bash
git add app/schemas/ app/dependencies.py
git commit -m "feat: Pydantic schemas and FastAPI dependencies"
```

---

## Task 5: Test Infrastructure

**Files:**
- Create: `pytest.ini`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create pytest.ini**

```ini
[pytest]
testpaths = tests
```

- [ ] **Step 2: Create tests/conftest.py**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db import Base, get_db
from app.main import app
from app.config import settings

SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
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
```

- [ ] **Step 3: Verify the test infrastructure works**

```bash
pytest tests/ -v
```

Expected: 0 tests collected, no errors.

- [ ] **Step 4: Commit**

```bash
git add pytest.ini tests/conftest.py tests/__init__.py tests/test_services/__init__.py tests/test_api/__init__.py
git commit -m "feat: test infrastructure with SQLite in-memory fixtures"
```

---

## Task 6: UserService + AuthService

**Files:**
- Create: `app/services/user_service.py`
- Create: `app/services/auth_service.py`
- Create: `tests/test_services/test_user_service.py`
- Create: `tests/test_services/test_auth_service.py`

- [ ] **Step 1: Write failing tests for user_service**

```python
# tests/test_services/test_user_service.py
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
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_services/test_user_service.py -v
```

Expected: ImportError or ModuleNotFoundError.

- [ ] **Step 3: Create app/services/user_service.py**

```python
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User, UserRole

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return _pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)

def create_user(db: Session, username: str, password: str, role: UserRole = UserRole.user) -> User:
    user = User(username=username, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def list_users(db: Session):
    return db.query(User).all()

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_services/test_user_service.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Write failing tests for auth_service**

```python
# tests/test_services/test_auth_service.py
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
```

- [ ] **Step 6: Run tests — verify they fail**

```bash
pytest tests/test_services/test_auth_service.py -v
```

Expected: ImportError.

- [ ] **Step 7: Create app/services/auth_service.py**

```python
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
```

- [ ] **Step 8: Run tests — verify they pass**

```bash
pytest tests/test_services/test_auth_service.py -v
```

Expected: 3 passed.

- [ ] **Step 9: Commit**

```bash
git add app/services/user_service.py app/services/auth_service.py tests/test_services/
git commit -m "feat: UserService and AuthService with tests"
```

---

## Task 7: Auth HTML Routes + Login Template

**Files:**
- Create: `app/routes/html/auth.py`
- Create: `app/templates/login.html`
- Modify: `app/main.py`

- [ ] **Step 1: Create app/routes/html/auth.py**

```python
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services import auth_service

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña incorrectos"},
            status_code=401,
        )
    auth_service.login(request, user)
    return RedirectResponse("/", status_code=303)

@router.post("/logout")
def logout(request: Request):
    auth_service.logout(request)
    return RedirectResponse("/login", status_code=303)
```

- [ ] **Step 2: Create app/templates/login.html**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>EnviroWatch — Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container d-flex justify-content-center align-items-center" style="min-height:100vh">
    <div class="card shadow" style="width:360px">
        <div class="card-body p-4">
            <h4 class="card-title mb-4 text-center">EnviroWatch</h4>
            {% if error %}
            <div class="alert alert-danger py-2">{{ error }}</div>
            {% endif %}
            <form method="post" action="/login">
                <div class="mb-3">
                    <label class="form-label">Usuario</label>
                    <input type="text" name="username" class="form-control" required autofocus>
                </div>
                <div class="mb-3">
                    <label class="form-label">Contraseña</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Ingresar</button>
            </form>
        </div>
    </div>
</div>
</body>
</html>
```

- [ ] **Step 3: Register router in app/main.py**

```python
# Add at the bottom of app/main.py:
from app.routes.html import auth as html_auth
app.include_router(html_auth.router)
```

- [ ] **Step 4: Create an admin user to test with**

Start the server: `uvicorn app.main:app --reload`

Then run this one-time script to seed the admin user:

```python
# seed_admin.py (run once, then delete)
from app.db import SessionLocal
from app.services.user_service import create_user
from app.models.user import UserRole

db = SessionLocal()
create_user(db, username="admin", password="admin123", role=UserRole.admin)
db.close()
print("Admin user created.")
```

```bash
python seed_admin.py
```

- [ ] **Step 5: Verify login works in browser**

Open `http://localhost:8000/login`, log in with `admin/admin123`. Should redirect to `/` (404 is expected since the dashboard doesn't exist yet). Logging in with wrong credentials should show the error message.

- [ ] **Step 6: Commit**

```bash
git add app/routes/html/auth.py app/templates/login.html app/main.py
git commit -m "feat: auth routes and login template"
```

---

## Task 8: RoomService + DeviceService

**Files:**
- Create: `app/services/room_service.py`
- Create: `app/services/device_service.py`
- Create: `tests/test_services/test_room_service.py`
- Create: `tests/test_services/test_device_service.py`

- [ ] **Step 1: Write failing tests for room_service**

```python
# tests/test_services/test_room_service.py
from app.services.room_service import create_room, list_rooms, get_room

def test_create_room(db):
    room = create_room(db, name="Lab A", location="Building 1, Floor 2")
    assert room.id is not None
    assert room.name == "Lab A"

def test_list_rooms(db):
    create_room(db, name="R1", location="L1")
    create_room(db, name="R2", location="L2")
    rooms = list_rooms(db)
    assert len(rooms) == 2

def test_get_room(db):
    room = create_room(db, name="Target", location="Loc")
    found = get_room(db, room.id)
    assert found is not None
    assert found.name == "Target"

def test_get_room_not_found(db):
    assert get_room(db, 9999) is None
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_services/test_room_service.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create app/services/room_service.py**

```python
from sqlalchemy.orm import Session
from app.models.room import Room

def create_room(db: Session, name: str, location: str) -> Room:
    room = Room(name=name, location=location)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def list_rooms(db: Session):
    return db.query(Room).all()

def get_room(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_services/test_room_service.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Write failing tests for device_service**

```python
# tests/test_services/test_device_service.py
from app.services.room_service import create_room
from app.services.device_service import create_device, list_devices, get_device, set_status, delete_device
from app.models.device import DeviceStatus

def test_create_device(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="Node 1")
    assert device.id is not None
    assert device.room_id == room.id
    assert device.status == DeviceStatus.offline

def test_list_devices(db):
    room = create_room(db, name="R", location="L")
    create_device(db, room_id=room.id, name="N1")
    create_device(db, room_id=room.id, name="N2")
    assert len(list_devices(db)) == 2

def test_get_device(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    found = get_device(db, device.id)
    assert found is not None

def test_get_device_not_found(db):
    assert get_device(db, 9999) is None

def test_set_status(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    updated = set_status(db, device.id, DeviceStatus.online)
    assert updated.status == DeviceStatus.online

def test_delete_device(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    assert delete_device(db, device.id) is True
    assert get_device(db, device.id) is None

def test_delete_device_not_found(db):
    assert delete_device(db, 9999) is False
```

- [ ] **Step 6: Run tests — verify they fail**

```bash
pytest tests/test_services/test_device_service.py -v
```

Expected: ImportError.

- [ ] **Step 7: Create app/services/device_service.py**

```python
from sqlalchemy.orm import Session
from app.models.device import Device, DeviceStatus

def create_device(db: Session, room_id: int, name: str) -> Device:
    device = Device(room_id=room_id, name=name)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device

def list_devices(db: Session):
    return db.query(Device).all()

def get_device(db: Session, device_id: int):
    return db.query(Device).filter(Device.id == device_id).first()

def set_status(db: Session, device_id: int, status: DeviceStatus):
    device = get_device(db, device_id)
    if device:
        device.status = status
        db.commit()
        db.refresh(device)
    return device

def delete_device(db: Session, device_id: int) -> bool:
    device = get_device(db, device_id)
    if not device:
        return False
    db.delete(device)
    db.commit()
    return True
```

- [ ] **Step 8: Run tests — verify they pass**

```bash
pytest tests/test_services/test_room_service.py tests/test_services/test_device_service.py -v
```

Expected: 11 passed.

- [ ] **Step 9: Commit**

```bash
git add app/services/room_service.py app/services/device_service.py tests/test_services/
git commit -m "feat: RoomService and DeviceService with tests"
```

---

## Task 9: API Routes — Devices

**Files:**
- Create: `app/routes/api/devices.py`
- Create: `tests/test_api/test_devices.py`
- Modify: `app/main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_api/test_devices.py
from app.services.room_service import create_room
from app.services.user_service import create_user
from app.models.user import UserRole

def test_list_devices_requires_auth(client):
    resp = client.get("/api/devices")
    assert resp.status_code == 401

def test_list_devices_empty(authed_client, db):
    resp = authed_client.get("/api/devices")
    assert resp.status_code == 200
    assert resp.json() == []

def test_create_device_requires_admin(client, db):
    room = create_room(db, name="R", location="L")
    create_user(db, username="regular", password="pass", role=UserRole.user)
    client.post("/login", data={"username": "regular", "password": "pass"}, follow_redirects=False)
    resp = client.post("/api/devices", json={"room_id": room.id, "name": "Node"})
    assert resp.status_code == 403

def test_create_device(authed_client, db):
    room = create_room(db, name="Lab", location="Floor 1")
    resp = authed_client.post("/api/devices", json={"room_id": room.id, "name": "Node 1"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Node 1"
    assert data["room_id"] == room.id
    assert data["status"] == "offline"

def test_list_devices_after_create(authed_client, db):
    room = create_room(db, name="R", location="L")
    authed_client.post("/api/devices", json={"room_id": room.id, "name": "N1"})
    authed_client.post("/api/devices", json={"room_id": room.id, "name": "N2"})
    resp = authed_client.get("/api/devices")
    assert len(resp.json()) == 2
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_api/test_devices.py -v
```

Expected: errors since router doesn't exist yet.

- [ ] **Step 3: Create app/routes/api/devices.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user, require_admin
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services import device_service

router = APIRouter(prefix="/api/devices", tags=["api-devices"])

@router.get("", response_model=list[DeviceResponse])
def list_devices(db: Session = Depends(get_db), _=Depends(require_user)):
    return device_service.list_devices(db)

@router.post("", response_model=DeviceResponse, status_code=201)
def create_device(body: DeviceCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return device_service.create_device(db, room_id=body.room_id, name=body.name)
```

- [ ] **Step 4: Register router in app/main.py**

```python
# Add to app/main.py:
from app.routes.api import devices as api_devices
app.include_router(api_devices.router)
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_api/test_devices.py -v
```

Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add app/routes/api/devices.py app/main.py tests/test_api/test_devices.py
git commit -m "feat: API routes for devices with tests"
```

---

## Task 10: MeasurementService

**Files:**
- Create: `app/services/measurement_service.py`
- Create: `tests/test_services/test_measurement_service.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_services/test_measurement_service.py
from datetime import datetime, timedelta, timezone
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.services.measurement_service import create_measurement, get_last_24h, get_latest
from app.models.device import DeviceStatus

def _make_device(db):
    room = create_room(db, name="R", location="L")
    return create_device(db, room_id=room.id, name="N")

def test_create_measurement(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    m = create_measurement(db, device_id=device.id, temperature=22.5, humidity=55.0, timestamp=now)
    assert m.id is not None
    assert m.temperature == 22.5

def test_create_measurement_sets_device_online(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=22.5, humidity=55.0, timestamp=now)
    db.refresh(device)
    assert device.status == DeviceStatus.online

def test_get_last_24h_returns_recent(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=20.0, humidity=50.0, timestamp=now - timedelta(hours=1))
    create_measurement(db, device_id=device.id, temperature=21.0, humidity=51.0, timestamp=now - timedelta(hours=23))
    results = get_last_24h(db, device.id)
    assert len(results) == 2

def test_get_last_24h_excludes_old(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=20.0, humidity=50.0, timestamp=now - timedelta(hours=25))
    results = get_last_24h(db, device.id)
    assert len(results) == 0

def test_get_latest(db):
    device = _make_device(db)
    now = datetime.now(timezone.utc)
    create_measurement(db, device_id=device.id, temperature=20.0, humidity=50.0, timestamp=now - timedelta(hours=2))
    create_measurement(db, device_id=device.id, temperature=25.0, humidity=60.0, timestamp=now)
    latest = get_latest(db, device.id)
    assert latest.temperature == 25.0

def test_get_latest_no_measurements(db):
    device = _make_device(db)
    assert get_latest(db, device.id) is None
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_services/test_measurement_service.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create app/services/measurement_service.py**

```python
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.measurement import Measurement
from app.models.device import DeviceStatus
from app.services import device_service

def create_measurement(db: Session, device_id: int, temperature: float, humidity: float, timestamp: datetime) -> Measurement:
    measurement = Measurement(device_id=device_id, temperature=temperature, humidity=humidity, timestamp=timestamp)
    db.add(measurement)
    device_service.set_status(db, device_id, DeviceStatus.online)
    db.commit()
    db.refresh(measurement)
    return measurement

def get_last_24h(db: Session, device_id: int):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    return (
        db.query(Measurement)
        .filter(Measurement.device_id == device_id, Measurement.timestamp >= cutoff)
        .order_by(Measurement.timestamp)
        .all()
    )

def get_latest(db: Session, device_id: int):
    return (
        db.query(Measurement)
        .filter(Measurement.device_id == device_id)
        .order_by(Measurement.timestamp.desc())
        .first()
    )
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_services/test_measurement_service.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add app/services/measurement_service.py tests/test_services/test_measurement_service.py
git commit -m "feat: MeasurementService with tests"
```

---

## Task 11: API Routes — Measurements (Sensor Ingestion)

**Files:**
- Create: `app/routes/api/measurements.py`
- Create: `tests/test_api/test_measurements.py`
- Modify: `app/main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_api/test_measurements.py
from datetime import datetime, timezone
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.config import settings

SENSOR_HEADERS = {"Authorization": f"Bearer {settings.sensor_token}"}

def _setup(db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    return device

def test_post_measurement_requires_token(client, db):
    device = _setup(db)
    payload = {"temperature": 22.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post(f"/api/devices/{device.id}/measurements", json=payload)
    assert resp.status_code == 401

def test_post_measurement_invalid_token(client, db):
    device = _setup(db)
    payload = {"temperature": 22.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post(f"/api/devices/{device.id}/measurements", json=payload, headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401

def test_post_measurement_success(client, db):
    device = _setup(db)
    payload = {"temperature": 23.5, "humidity": 60.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post(f"/api/devices/{device.id}/measurements", json=payload, headers=SENSOR_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["temperature"] == 23.5
    assert data["device_id"] == device.id

def test_post_measurement_device_not_found(client, db):
    payload = {"temperature": 22.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc).isoformat()}
    resp = client.post("/api/devices/9999/measurements", json=payload, headers=SENSOR_HEADERS)
    assert resp.status_code == 404

def test_get_measurements_requires_auth(client, db):
    device = _setup(db)
    resp = client.get(f"/api/devices/{device.id}/measurements")
    assert resp.status_code == 401

def test_get_measurements_empty(authed_client, db):
    device = _setup(db)
    resp = authed_client.get(f"/api/devices/{device.id}/measurements")
    assert resp.status_code == 200
    assert resp.json() == []
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_api/test_measurements.py -v
```

Expected: errors since router doesn't exist.

- [ ] **Step 3: Create app/routes/api/measurements.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user, verify_sensor_token
from app.schemas.measurement import MeasurementCreate, MeasurementResponse
from app.services import measurement_service, device_service

router = APIRouter(prefix="/api/devices", tags=["api-measurements"])

@router.post("/{device_id}/measurements", response_model=MeasurementResponse, status_code=201)
def create_measurement(
    device_id: int,
    body: MeasurementCreate,
    db: Session = Depends(get_db),
    _=Depends(verify_sensor_token),
):
    if not device_service.get_device(db, device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    return measurement_service.create_measurement(
        db, device_id=device_id, temperature=body.temperature,
        humidity=body.humidity, timestamp=body.timestamp,
    )

@router.get("/{device_id}/measurements", response_model=list[MeasurementResponse])
def get_measurements(
    device_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    if not device_service.get_device(db, device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    return measurement_service.get_last_24h(db, device_id)
```

- [ ] **Step 4: Register router in app/main.py**

```python
# Add to app/main.py:
from app.routes.api import measurements as api_measurements
app.include_router(api_measurements.router)
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_api/test_measurements.py -v
```

Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add app/routes/api/measurements.py app/main.py tests/test_api/test_measurements.py
git commit -m "feat: measurement API routes for sensor ingestion with tests"
```

---

## Task 12: ThresholdService

**Files:**
- Create: `app/services/threshold_service.py`
- Create: `tests/test_services/test_threshold_service.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_services/test_threshold_service.py
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.services.threshold_service import get_by_device, upsert

def _make_device(db):
    room = create_room(db, name="R", location="L")
    return create_device(db, room_id=room.id, name="N")

def test_get_by_device_none(db):
    device = _make_device(db)
    assert get_by_device(db, device.id) is None

def test_upsert_creates(db):
    device = _make_device(db)
    t = upsert(db, device_id=device.id, temp_min=18.0, temp_max=26.0, humidity_min=40.0, humidity_max=70.0)
    assert t.id is not None
    assert t.temp_min == 18.0

def test_upsert_updates(db):
    device = _make_device(db)
    upsert(db, device_id=device.id, temp_min=18.0, temp_max=26.0, humidity_min=40.0, humidity_max=70.0)
    updated = upsert(db, device_id=device.id, temp_min=20.0, temp_max=28.0, humidity_min=45.0, humidity_max=75.0)
    assert updated.temp_min == 20.0
    # Still only one threshold record
    assert get_by_device(db, device.id).temp_max == 28.0
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_services/test_threshold_service.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create app/services/threshold_service.py**

```python
from sqlalchemy.orm import Session
from app.models.threshold import Threshold

def get_by_device(db: Session, device_id: int):
    return db.query(Threshold).filter(Threshold.device_id == device_id).first()

def upsert(db: Session, device_id: int, temp_min: float, temp_max: float, humidity_min: float, humidity_max: float) -> Threshold:
    threshold = get_by_device(db, device_id)
    if threshold:
        threshold.temp_min = temp_min
        threshold.temp_max = temp_max
        threshold.humidity_min = humidity_min
        threshold.humidity_max = humidity_max
    else:
        threshold = Threshold(
            device_id=device_id, temp_min=temp_min, temp_max=temp_max,
            humidity_min=humidity_min, humidity_max=humidity_max,
        )
        db.add(threshold)
    db.commit()
    db.refresh(threshold)
    return threshold
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_services/test_threshold_service.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add app/services/threshold_service.py tests/test_services/test_threshold_service.py
git commit -m "feat: ThresholdService with tests"
```

---

## Task 13: AlertService

**Files:**
- Create: `app/services/alert_service.py`
- Create: `tests/test_services/test_alert_service.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_services/test_alert_service.py
from datetime import datetime, timezone
from unittest.mock import MagicMock
from app.services.alert_service import compute_status

def _mock_measurement(temp, humidity):
    m = MagicMock()
    m.temperature = temp
    m.humidity = humidity
    return m

def _mock_threshold(temp_min, temp_max, hum_min, hum_max):
    t = MagicMock()
    t.temp_min = temp_min
    t.temp_max = temp_max
    t.humidity_min = hum_min
    t.humidity_max = hum_max
    return t

# Threshold: temp 20-30°C, humidity 40-70% (ranges: 10°C, 30%)
# Yellow zone: temp 20-21 or 29-30; humidity 40-43 or 67-70

def test_unknown_no_measurement():
    assert compute_status(None, _mock_threshold(20, 30, 40, 70)) == "unknown"

def test_unknown_no_threshold():
    assert compute_status(_mock_measurement(25, 55), None) == "unknown"

def test_green():
    assert compute_status(_mock_measurement(25, 55), _mock_threshold(20, 30, 40, 70)) == "green"

def test_red_temp_above():
    assert compute_status(_mock_measurement(31, 55), _mock_threshold(20, 30, 40, 70)) == "red"

def test_red_temp_below():
    assert compute_status(_mock_measurement(19, 55), _mock_threshold(20, 30, 40, 70)) == "red"

def test_red_humidity_above():
    assert compute_status(_mock_measurement(25, 71), _mock_threshold(20, 30, 40, 70)) == "red"

def test_red_humidity_below():
    assert compute_status(_mock_measurement(25, 39), _mock_threshold(20, 30, 40, 70)) == "red"

def test_yellow_temp_near_max():
    # 29.5°C is within 10% of range (1°C) from max
    assert compute_status(_mock_measurement(29.5, 55), _mock_threshold(20, 30, 40, 70)) == "yellow"

def test_yellow_humidity_near_min():
    # 41.5% is within 10% of range (3%) from min
    assert compute_status(_mock_measurement(25, 41.5), _mock_threshold(20, 30, 40, 70)) == "yellow"
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_services/test_alert_service.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create app/services/alert_service.py**

```python
from typing import Literal

AlertStatus = Literal["green", "yellow", "red", "unknown"]

def compute_status(measurement, threshold) -> AlertStatus:
    if measurement is None or threshold is None:
        return "unknown"

    temp_range = threshold.temp_max - threshold.temp_min
    hum_range = threshold.humidity_max - threshold.humidity_min
    temp_margin = temp_range * 0.1
    hum_margin = hum_range * 0.1

    temp_out = measurement.temperature < threshold.temp_min or measurement.temperature > threshold.temp_max
    hum_out = measurement.humidity < threshold.humidity_min or measurement.humidity > threshold.humidity_max

    if temp_out or hum_out:
        return "red"

    temp_near = (
        measurement.temperature <= threshold.temp_min + temp_margin
        or measurement.temperature >= threshold.temp_max - temp_margin
    )
    hum_near = (
        measurement.humidity <= threshold.humidity_min + hum_margin
        or measurement.humidity >= threshold.humidity_max - hum_margin
    )

    if temp_near or hum_near:
        return "yellow"

    return "green"
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_services/test_alert_service.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Run the full test suite**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add app/services/alert_service.py tests/test_services/test_alert_service.py
git commit -m "feat: AlertService with tests"
```

---

## Task 14: API Route — Room Status

**Files:**
- Create: `app/routes/api/rooms.py`
- Create: `tests/test_api/test_rooms_api.py`
- Modify: `app/main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_api/test_rooms_api.py
from datetime import datetime, timezone
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.services.measurement_service import create_measurement
from app.services.threshold_service import upsert as upsert_threshold
from app.config import settings

SENSOR_HEADERS = {"Authorization": f"Bearer {settings.sensor_token}"}

def test_room_status_requires_auth(client, db):
    room = create_room(db, name="R", location="L")
    resp = client.get(f"/api/rooms/{room.id}/status")
    assert resp.status_code == 401

def test_room_status_not_found(authed_client, db):
    resp = authed_client.get("/api/rooms/9999/status")
    assert resp.status_code == 404

def test_room_status_unknown_no_device(authed_client, db):
    room = create_room(db, name="Empty Room", location="L")
    resp = authed_client.get(f"/api/rooms/{room.id}/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unknown"

def test_room_status_green(authed_client, db):
    room = create_room(db, name="R", location="L")
    device = create_device(db, room_id=room.id, name="N")
    upsert_threshold(db, device_id=device.id, temp_min=20.0, temp_max=30.0, humidity_min=40.0, humidity_max=70.0)
    create_measurement(db, device_id=device.id, temperature=25.0, humidity=55.0, timestamp=datetime.now(timezone.utc))
    resp = authed_client.get(f"/api/rooms/{room.id}/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "green"
    assert data["temperature"] == 25.0
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_api/test_rooms_api.py -v
```

Expected: errors since router doesn't exist.

- [ ] **Step 3: Create app/routes/api/rooms.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_user
from app.models.device import Device
from app.services import room_service, measurement_service, threshold_service, alert_service

router = APIRouter(prefix="/api/rooms", tags=["api-rooms"])

@router.get("/{room_id}/status")
def get_room_status(room_id: int, db: Session = Depends(get_db), _=Depends(require_user)):
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    device = db.query(Device).filter(Device.room_id == room_id).first()
    if not device:
        return {"room_id": room_id, "status": "unknown", "temperature": None, "humidity": None, "timestamp": None}

    latest = measurement_service.get_latest(db, device.id)
    threshold = threshold_service.get_by_device(db, device.id)
    status = alert_service.compute_status(latest, threshold)

    return {
        "room_id": room_id,
        "device_id": device.id,
        "status": status,
        "temperature": latest.temperature if latest else None,
        "humidity": latest.humidity if latest else None,
        "timestamp": latest.timestamp.isoformat() if latest else None,
    }
```

- [ ] **Step 4: Register router in app/main.py**

```python
# Add to app/main.py:
from app.routes.api import rooms as api_rooms
app.include_router(api_rooms.router)
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_api/ -v
```

Expected: all API tests pass.

- [ ] **Step 6: Commit**

```bash
git add app/routes/api/rooms.py app/main.py tests/test_api/test_rooms_api.py
git commit -m "feat: room status API route with tests"
```

---

## Task 15: Base Template + Dashboard

**Files:**
- Create: `app/templates/base.html`
- Create: `app/templates/dashboard.html`
- Create: `app/routes/html/dashboard.py`
- Modify: `app/main.py`

- [ ] **Step 1: Create app/templates/base.html**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>EnviroWatch</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/custom.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="/">EnviroWatch</a>
        <div class="navbar-nav ms-auto align-items-center">
            {% if username %}
            <a class="nav-link" href="/config">Configuración</a>
            {% if role == "admin" %}
            <a class="nav-link" href="/users">Usuarios</a>
            {% endif %}
            <span class="navbar-text me-3 text-white-50">{{ username }}</span>
            <form method="post" action="/logout" class="d-inline">
                <button type="submit" class="btn btn-outline-light btn-sm">Salir</button>
            </form>
            {% endif %}
        </div>
    </div>
</nav>
<main class="container mt-4">
    {% block content %}{% endblock %}
</main>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
{% block scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Create app/templates/dashboard.html**

```html
{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Dashboard</h2>
{% if not rooms %}
<div class="alert alert-info">No hay habitaciones registradas.</div>
{% else %}
<div class="row row-cols-1 row-cols-md-3 g-4">
{% for item in rooms %}
{% set color = "success" if item.status == "green" else "warning" if item.status == "yellow" else "danger" if item.status == "red" else "secondary" %}
<div class="col">
    <div class="card h-100 border-{{ color }}">
        <div class="card-header bg-{{ color }} text-white d-flex justify-content-between align-items-center">
            <span>{{ item.room.name }}</span>
            <span class="badge bg-white text-{{ color }}">{{ item.status }}</span>
        </div>
        <div class="card-body">
            <p class="text-muted mb-1">{{ item.room.location }}</p>
            {% if item.latest %}
            <p class="mb-1"><strong>Temp:</strong> {{ "%.1f"|format(item.latest.temperature) }} °C</p>
            <p class="mb-0"><strong>Humedad:</strong> {{ "%.1f"|format(item.latest.humidity) }} %</p>
            {% else %}
            <p class="text-muted">Sin mediciones recientes</p>
            {% endif %}
        </div>
        <div class="card-footer bg-transparent">
            <a href="/rooms/{{ item.room.id }}" class="btn btn-sm btn-outline-primary">Ver detalle</a>
        </div>
    </div>
</div>
{% endfor %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Create app/routes/html/dashboard.py**

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db
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
```

- [ ] **Step 4: Register router in app/main.py**

```python
# Add to app/main.py:
from app.routes.html import dashboard as html_dashboard
app.include_router(html_dashboard.router)
```

- [ ] **Step 5: Verify in browser**

Start the server: `uvicorn app.main:app --reload`

Log in and verify the dashboard loads at `http://localhost:8000/`. If there are rooms in the database, cards should appear with correct status colors.

- [ ] **Step 6: Commit**

```bash
git add app/templates/base.html app/templates/dashboard.html app/routes/html/dashboard.py app/main.py
git commit -m "feat: base template and dashboard page"
```

---

## Task 16: Room Detail Page

**Files:**
- Create: `app/templates/room_detail.html`
- Create: `app/routes/html/rooms.py`
- Modify: `app/main.py`

- [ ] **Step 1: Create app/templates/room_detail.html**

```html
{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <div>
        <h2>{{ room.name }}</h2>
        <p class="text-muted mb-0">{{ room.location }}</p>
    </div>
    <a href="/" class="btn btn-outline-secondary btn-sm">← Dashboard</a>
</div>

{% set color = "success" if status == "green" else "warning" if status == "yellow" else "danger" if status == "red" else "secondary" %}
<div class="row g-3 mb-4">
    <div class="col-md-4">
        <div class="card text-center border-{{ color }}">
            <div class="card-body">
                <h6 class="card-subtitle mb-2 text-muted">Estado</h6>
                <span class="badge bg-{{ color }} fs-6 px-3 py-2">{{ status }}</span>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card text-center">
            <div class="card-body">
                <h6 class="card-subtitle mb-2 text-muted">Temperatura</h6>
                <p class="fs-2 mb-0">{{ "%.1f"|format(latest.temperature) if latest else "--" }} <small>°C</small></p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card text-center">
            <div class="card-body">
                <h6 class="card-subtitle mb-2 text-muted">Humedad</h6>
                <p class="fs-2 mb-0">{{ "%.1f"|format(latest.humidity) if latest else "--" }} <small>%</small></p>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <h5 class="card-title">Historial últimas 24 horas</h5>
        {% if timestamps %}
        <canvas id="historyChart" height="80"></canvas>
        {% else %}
        <p class="text-muted">Sin datos en las últimas 24 horas.</p>
        {% endif %}
    </div>
</div>
{% endblock %}

{% block scripts %}
{% if timestamps %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
new Chart(document.getElementById("historyChart"), {
    type: "line",
    data: {
        labels: {{ timestamps | tojson }},
        datasets: [
            {
                label: "Temperatura (°C)",
                data: {{ temperatures | tojson }},
                borderColor: "rgb(220, 53, 69)",
                backgroundColor: "rgba(220, 53, 69, 0.1)",
                tension: 0.3,
                fill: true
            },
            {
                label: "Humedad (%)",
                data: {{ humidities | tojson }},
                borderColor: "rgb(13, 110, 253)",
                backgroundColor: "rgba(13, 110, 253, 0.1)",
                tension: 0.3,
                fill: true,
                yAxisID: "y2"
            }
        ]
    },
    options: {
        responsive: true,
        interaction: { mode: "index", intersect: false },
        scales: {
            y: { title: { display: true, text: "°C" } },
            y2: { position: "right", title: { display: true, text: "%" }, grid: { drawOnChartArea: false } }
        }
    }
});
</script>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: Create app/routes/html/rooms.py**

```python
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.device import Device
from app.services import room_service, measurement_service, threshold_service, alert_service

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/rooms/{room_id}", response_class=HTMLResponse)
def room_detail(room_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)

    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    device = db.query(Device).filter(Device.room_id == room_id).first()
    latest, status = None, "unknown"
    timestamps, temperatures, humidities = [], [], []

    if device:
        latest = measurement_service.get_latest(db, device.id)
        threshold = threshold_service.get_by_device(db, device.id)
        status = alert_service.compute_status(latest, threshold)
        history = measurement_service.get_last_24h(db, device.id)
        timestamps = [m.timestamp.strftime("%H:%M") for m in history]
        temperatures = [m.temperature for m in history]
        humidities = [m.humidity for m in history]

    return templates.TemplateResponse("room_detail.html", {
        "request": request,
        "room": room,
        "latest": latest,
        "status": status,
        "timestamps": timestamps,
        "temperatures": temperatures,
        "humidities": humidities,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })
```

- [ ] **Step 3: Register router in app/main.py**

```python
# Add to app/main.py:
from app.routes.html import rooms as html_rooms
app.include_router(html_rooms.router)
```

- [ ] **Step 4: Verify in browser**

Navigate from the dashboard to a room detail page. Verify the status card shows the correct color and the chart renders if measurements exist.

- [ ] **Step 5: Commit**

```bash
git add app/templates/room_detail.html app/routes/html/rooms.py app/main.py
git commit -m "feat: room detail page with Chart.js 24h graph"
```

---

## Task 17: Config Page (Threshold Management)

**Files:**
- Create: `app/templates/config.html`
- Create: `app/routes/html/config.py`
- Modify: `app/main.py`

- [ ] **Step 1: Create app/templates/config.html**

```html
{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Configuración de límites</h2>
{% if message %}
<div class="alert alert-success alert-dismissible fade show" role="alert">
    {{ message }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
{% endif %}
{% if not devices %}
<div class="alert alert-info">No hay dispositivos registrados.</div>
{% else %}
<div class="row g-4">
{% for item in devices %}
<div class="col-md-6">
    <div class="card">
        <div class="card-header">
            <strong>{{ item.device.name }}</strong>
            <span class="text-muted ms-2">— {{ item.room.name }}</span>
        </div>
        <div class="card-body">
            <form method="post" action="/config/{{ item.device.id }}">
                <div class="row g-2">
                    <div class="col-6">
                        <label class="form-label">Temp. mín (°C)</label>
                        <input type="number" step="0.1" name="temp_min" class="form-control"
                               value="{{ item.threshold.temp_min if item.threshold else '' }}" required>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Temp. máx (°C)</label>
                        <input type="number" step="0.1" name="temp_max" class="form-control"
                               value="{{ item.threshold.temp_max if item.threshold else '' }}" required>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Humedad mín (%)</label>
                        <input type="number" step="0.1" name="humidity_min" class="form-control"
                               value="{{ item.threshold.humidity_min if item.threshold else '' }}" required>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Humedad máx (%)</label>
                        <input type="number" step="0.1" name="humidity_max" class="form-control"
                               value="{{ item.threshold.humidity_max if item.threshold else '' }}" required>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary btn-sm mt-3">Guardar</button>
            </form>
        </div>
    </div>
</div>
{% endfor %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: Create app/routes/html/config.py**

```python
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.device import Device
from app.models.room import Room
from app.services import threshold_service

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/config", response_class=HTMLResponse)
def config_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)

    devices = db.query(Device).all()
    items = []
    for device in devices:
        room = db.query(Room).filter(Room.id == device.room_id).first()
        threshold = threshold_service.get_by_device(db, device.id)
        items.append({"device": device, "room": room, "threshold": threshold})

    return templates.TemplateResponse("config.html", {
        "request": request,
        "devices": items,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })

@router.post("/config/{device_id}")
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

    threshold_service.upsert(
        db, device_id=device_id,
        temp_min=temp_min, temp_max=temp_max,
        humidity_min=humidity_min, humidity_max=humidity_max,
    )
    return RedirectResponse("/config?saved=1", status_code=303)
```

- [ ] **Step 3: Update config_page to pass success message**

Replace the `config_page` function with the following (adds the `message` variable to context):

```python
@router.get("/config", response_class=HTMLResponse)
def config_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)

    message = "Configuración guardada." if request.query_params.get("saved") else None
    devices = db.query(Device).all()
    items = []
    for device in devices:
        room = db.query(Room).filter(Room.id == device.room_id).first()
        threshold = threshold_service.get_by_device(db, device.id)
        items.append({"device": device, "room": room, "threshold": threshold})

    return templates.TemplateResponse("config.html", {
        "request": request,
        "devices": items,
        "message": message,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })
```

- [ ] **Step 4: Register router in app/main.py**

```python
# Add to app/main.py:
from app.routes.html import config as html_config
app.include_router(html_config.router)
```

- [ ] **Step 5: Verify in browser**

Navigate to `http://localhost:8000/config`. Edit thresholds for a device and save. Verify the success banner appears and values persist on page reload.

- [ ] **Step 6: Commit**

```bash
git add app/templates/config.html app/routes/html/config.py app/main.py
git commit -m "feat: config page for threshold management"
```

---

## Task 18: Users Admin Page

**Files:**
- Create: `app/templates/users.html`
- Create: `app/routes/html/users.py`
- Modify: `app/main.py`

- [ ] **Step 1: Create app/templates/users.html**

```html
{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Gestión de usuarios</h2>

<div class="row g-4">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Usuarios registrados</div>
            <div class="card-body p-0">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr><th>Usuario</th><th>Rol</th><th>Creado</th><th></th></tr>
                    </thead>
                    <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user.username }}</td>
                        <td><span class="badge bg-{{ 'danger' if user.role == 'admin' else 'secondary' }}">{{ user.role }}</span></td>
                        <td class="text-muted small">{{ user.created_at.strftime("%Y-%m-%d") }}</td>
                        <td>
                            {% if user.id != current_user_id %}
                            <form method="post" action="/users/{{ user.id }}/delete" class="d-inline"
                                  onsubmit="return confirm('¿Eliminar {{ user.username }}?')">
                                <button type="submit" class="btn btn-outline-danger btn-sm">Eliminar</button>
                            </form>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-header">Nuevo usuario</div>
            <div class="card-body">
                {% if error %}
                <div class="alert alert-danger py-2">{{ error }}</div>
                {% endif %}
                <form method="post" action="/users">
                    <div class="mb-3">
                        <label class="form-label">Usuario</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Contraseña</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Rol</label>
                        <select name="role" class="form-select">
                            <option value="user">user</option>
                            <option value="admin">admin</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Crear usuario</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Create app/routes/html/users.py**

```python
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
```

- [ ] **Step 3: Register router in app/main.py**

```python
# Add to app/main.py:
from app.routes.html import users as html_users
app.include_router(html_users.router)
```

- [ ] **Step 4: Verify in browser**

Log in as admin and navigate to `http://localhost:8000/users`. Create a new user, verify it appears in the list. Log in as a non-admin and verify `/users` redirects to `/`.

- [ ] **Step 5: Run the full test suite one final time**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add app/templates/users.html app/routes/html/users.py app/main.py
git commit -m "feat: users admin page — list, create, delete"
```

---

## Final Verification

- [ ] Start the app: `uvicorn app.main:app --reload`
- [ ] Log in as admin
- [ ] Create a room and a device via the API (`POST /api/devices`)
- [ ] Post a measurement via sensor token (`POST /api/devices/{id}/measurements`)
- [ ] Configure thresholds on the Config page
- [ ] Verify the dashboard shows the correct status color
- [ ] Verify the room detail page shows current values and the 24h chart
- [ ] Create and delete a user from the Users page
- [ ] Check `/docs` for auto-generated OpenAPI documentation
