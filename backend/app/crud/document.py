from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.models.document import Document, ProcessingStatus


async def create_document(db: AsyncSession, filename: str, original_path: str, owner_id: int, document_type: str = "unknown") -> Document:
    doc = Document(
        filename=filename,
        original_path=original_path,
        owner_id=owner_id,
        document_type=document_type,
        status=ProcessingStatus.PENDING
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


async def get_document(db: AsyncSession, doc_id: int) -> Optional[Document]:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    return result.scalar_one_or_none()


async def list_documents(db: AsyncSession, owner_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Document]:
    query = select(Document)
    if owner_id is not None:
        query = query.where(Document.owner_id == owner_id)
    query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_document_status(db: AsyncSession, doc_id: int, status: ProcessingStatus, processed_text: Optional[str] = None) -> Optional[Document]:
    doc = await get_document(db, doc_id)
    if doc:
        doc.status = status
        if processed_text is not None:
            doc.processed_text = processed_text
        await db.flush()
        await db.refresh(doc)
    return doc


async def update_document_text(db: AsyncSession, doc_id: int, text: str) -> Optional[Document]:
    doc = await get_document(db, doc_id)
    if doc:
        doc.processed_text = text
        await db.flush()
        await db.refresh(doc)
    return doc
