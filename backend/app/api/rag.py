from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_doctor_or_admin, get_current_user
from app.models.user import User
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.rag_service import rag_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    request: Request,
    query_req: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    result = await rag_service.query(
        query=query_req.query,
        top_k=query_req.top_k,
        filters=query_req.filters
    )

    accessed_docs = list(set([c["document_id"] for c in result["retrieved_chunks"]]))

    await audit_service.log_action(
        db, current_user, "QUERY",
        resource_type="rag_query",
        query_text=query_req.query,
        accessed_documents=accessed_docs,
        details={"top_k": query_req.top_k, "latency_ms": result["latency_ms"]},
        request=request
    )

    return RAGQueryResponse(**result)
