from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.models.document import ProcessingStatus


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDetail(BaseModel):
    id: int
    filename: str
    document_type: str
    status: ProcessingStatus
    processed_text: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    id: int
    filename: str
    document_type: str
    status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True
