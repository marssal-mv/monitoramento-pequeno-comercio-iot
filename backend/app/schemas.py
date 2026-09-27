from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventCreate(BaseModel):
    sensor_id: str
    timestamp: datetime
    motion_detected: bool
    location: str = "porta"


class EventResponse(EventCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    total_events: int
    today_events: int
    alerts_out_of_hours: int
    last_motion: Optional[datetime] = None


class StatusResponse(BaseModel):
    status: str  # "normal", "movimento_recente", "alerta"
    last_motion: Optional[datetime]
    operational_hours: dict
    motion_in_last_30min: bool
