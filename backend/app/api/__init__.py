from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.entities import router as entities_router
from app.api.rag import router as rag_router
from app.api.audit import router as audit_router

__all__ = [
    "auth_router",
    "documents_router",
    "entities_router",
    "rag_router",
    "audit_router",
]
