from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from app.models.entity import EntityType


class CodeMappingSchema(BaseModel):
    id: int
    code_system: str
    code: str
    name: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClinicalEntitySchema(BaseModel):
    id: int
    entity_type: EntityType
    text: str
    normalized_name: Optional[str] = None
    confidence: Optional[float] = None
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    codes: List[CodeMappingSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractedEntitiesResponse(BaseModel):
    document_id: int
    entities: List[ClinicalEntitySchema]


class CodeMapRequest(BaseModel):
    entity_id: int


class EntityExtractionResult(BaseModel):
    entity_type: str
    text: str
    normalized_name: Optional[str] = None
    confidence: Optional[float] = None
