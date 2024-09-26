from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # LOGIN, UPLOAD, QUERY, VIEW, EXTRACT
    resource_type = Column(String)  # document, query, user
    resource_id = Column(Integer)
    details = Column(JSON, default=dict)
    query_text = Column(Text)
    accessed_documents = Column(JSON, default=list)
    ip_address = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
