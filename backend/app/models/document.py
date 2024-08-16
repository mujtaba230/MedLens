import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    OCR = "ocr"
    EXTRACTING = "extracting"
    MAPPING = "mapping"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    processed_text = Column(Text)
    document_type = Column(String, default="unknown")
    metadata_json = Column(JSON, default=dict)
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="documents")
    entities = relationship("ClinicalEntity", back_populates="document", cascade="all, delete-orphan")
