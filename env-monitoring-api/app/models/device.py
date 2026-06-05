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
