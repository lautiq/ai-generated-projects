import enum

from sqlalchemy import Column, Integer, String, DateTime, Enum, func

from app.db import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), nullable=False, default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
