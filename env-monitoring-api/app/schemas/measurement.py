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
