import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum

from app.core.database import Base
from sqlalchemy.orm import relationship


class UserRole(str, enum.Enum):
    DOCTOR = "doctor"
    ADMIN = "admin"
    AUDITOR = "auditor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.DOCTOR, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    documents = relationship("Document", back_populates="owner")
