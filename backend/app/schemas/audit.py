from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    details: Dict[str, Any] = {}
    query_text: Optional[str] = None
    accessed_documents: List[int] = []
    ip_address: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    username: str
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    details: Dict[str, Any]
    query_text: Optional[str]
    accessed_documents: List[int]
    ip_address: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
