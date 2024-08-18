import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class EntityType(str, enum.Enum):
    DIAGNOSIS = "diagnosis"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    SYMPTOM = "symptom"
    LAB_RESULT = "lab_result"


class ClinicalEntity(Base):
    __tablename__ = "clinical_entities"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    entity_type = Column(SQLEnum(EntityType), nullable=False)
    text = Column(Text, nullable=False)
    normalized_name = Column(String)
    confidence = Column(Float)
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="entities")
    codes = relationship("CodeMapping", back_populates="entity", cascade="all, delete-orphan")


class CodeMapping(Base):
    __tablename__ = "code_mappings"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("clinical_entities.id"), nullable=False)
    code_system = Column(String, nullable=False)  # ICD-10, CPT, SNOMED
    code = Column(String, nullable=False)
    name = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    entity = relationship("ClinicalEntity", back_populates="codes")
