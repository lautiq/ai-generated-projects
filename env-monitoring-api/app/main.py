from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.routes.html import auth as html_auth
from app.routes.api import devices as api_devices
from app.routes.api import measurements as api_measurements

app = FastAPI(title="EnviroWatch")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(html_auth.router)
app.include_router(api_devices.router)
app.include_router(api_measurements.router)
