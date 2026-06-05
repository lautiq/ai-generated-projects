from pydantic import BaseModel, Field, model_validator


class ThresholdUpsert(BaseModel):
    temp_min: float
    temp_max: float
    humidity_min: float = Field(ge=0, le=100)
    humidity_max: float = Field(ge=0, le=100)

    @model_validator(mode="after")
    def check_ranges(self):
        if self.temp_min >= self.temp_max:
            raise ValueError("temp_min must be less than temp_max")
        if self.humidity_min >= self.humidity_max:
            raise ValueError("humidity_min must be less than humidity_max")
        return self


class ThresholdResponse(BaseModel):
    id: int
    device_id: int
    temp_min: float
    temp_max: float
    humidity_min: float
    humidity_max: float

    model_config = {"from_attributes": True}
