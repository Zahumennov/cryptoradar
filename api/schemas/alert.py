from pydantic import BaseModel, field_validator
from datetime import datetime


class AlertCreate(BaseModel):
    coin: str
    threshold: float
    direction: str

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v):
        if v not in ("above", "below"):
            raise ValueError("direction must be 'above' or 'below'")
        return v

    @field_validator("coin")
    @classmethod
    def validate_coin(cls, v):
        return v.lower().strip()


class AlertResponse(BaseModel):
    id: int
    coin: str
    threshold: float
    direction: str
    is_active: bool
    triggered_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}