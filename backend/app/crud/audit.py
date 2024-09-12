from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.models.audit import AuditLog


async def create_audit_log(
    db: AsyncSession,
    user_id: int,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    query_text: Optional[str] = None,
    accessed_documents: Optional[List[int]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        query_text=query_text,
        accessed_documents=accessed_documents or [],
        ip_address=ip_address
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def list_audit_logs(
    db: AsyncSession,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.timestamp.desc())
    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action is not None:
        query = query.where(AuditLog.action == action)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
