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
