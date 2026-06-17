from pydantic import BaseModel, Field
from datetime import datetime


class RoomCreate(BaseModel):
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)


class RoomResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime

    model_config = {"from_attributes": True}
