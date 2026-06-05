from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, unique=True)
    temp_min = Column(Float, nullable=False)
    temp_max = Column(Float, nullable=False)
    humidity_min = Column(Float, nullable=False)
    humidity_max = Column(Float, nullable=False)

    device = relationship("Device", back_populates="threshold")
