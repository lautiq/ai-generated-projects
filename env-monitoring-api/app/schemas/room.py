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
