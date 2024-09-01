import asyncio
import os
import shutil
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_doctor_or_admin, get_current_user
from app.models.user import User
from app.models.document import ProcessingStatus
from app.crud.document import create_document, get_document, list_documents, update_document_status, update_document_text
from app.schemas.document import DocumentUploadResponse, DocumentDetail, DocumentListItem
from app.services.ocr_service import ocr_service
from app.services.rag_service import rag_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    def _save_file():
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return os.path.getsize(file_path)

    file_size = await asyncio.to_thread(_save_file)

    doc = await create_document(
        db,
        filename=file.filename,
        original_path=file_path,
        owner_id=current_user.id,
        document_type="pdf"
    )

    await audit_service.log_action(
        db, current_user, "UPLOAD",
        resource_type="document", resource_id=doc.id,
        details={"filename": file.filename, "size": file_size},
        request=request
    )

    return doc


@router.get("/", response_model=List[DocumentListItem])
async def list_user_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value == "admin":
        docs = await list_documents(db, skip=skip, limit=limit)
    else:
        docs = await list_documents(db, owner_id=current_user.id, skip=skip, limit=limit)
    return docs


@router.get("/{doc_id}", response_model=DocumentDetail)
async def get_document_detail(
    request: Request,
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = await get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role.value != "admin" and doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")

    await audit_service.log_action(
        db, current_user, "VIEW",
        resource_type="document", resource_id=doc.id,
        request=request
    )
    return doc


@router.post("/{doc_id}/process")
async def process_document(
    request: Request,
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    doc = await get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role.value != "admin" and doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await update_document_status(db, doc_id, ProcessingStatus.OCR)
    result = await asyncio.to_thread(ocr_service.process_pdf, doc.original_path)
    await update_document_text(db, doc_id, result["text"])
    await update_document_status(db, doc_id, ProcessingStatus.COMPLETED)

    # Index for RAG
    if result["text"]:
        await asyncio.to_thread(rag_service.index_document, doc_id, result["text"])

    await audit_service.log_action(
        db, current_user, "PROCESS",
        resource_type="document", resource_id=doc.id,
        details={"method": result["method"], "is_scanned": result["is_scanned"]},
        request=request
    )

    return {"document_id": doc_id, "status": "completed", "method": result["method"], "text_length": len(result["text"])}
