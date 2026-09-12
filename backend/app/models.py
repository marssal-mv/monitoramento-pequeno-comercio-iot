from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .database import Base


class SensorEvent(Base):
    """Evento de movimento reportado por um sensor (ESP32)."""

    __tablename__ = "sensor_events"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    motion_detected = Column(Boolean, default=True, nullable=False)
    location = Column(String, default="porta", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
