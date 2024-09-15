from typing import Optional, List
from fastapi import Request

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.audit import create_audit_log
from app.models.user import User


class AuditService:
    async def log_action(
        self,
        db: AsyncSession,
        user: User,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[dict] = None,
        query_text: Optional[str] = None,
        accessed_documents: Optional[List[int]] = None,
        request: Optional[Request] = None
    ):
        ip_address = None
        if request:
            forwarded = request.headers.get("x-forwarded-for")
            ip_address = forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else None

        await create_audit_log(
            db=db,
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            query_text=query_text,
            accessed_documents=accessed_documents or [],
            ip_address=ip_address
        )


audit_service = AuditService()
