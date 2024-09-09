from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.models.entity import ClinicalEntity, CodeMapping, EntityType


async def create_clinical_entity(
    db: AsyncSession,
    document_id: int,
    entity_type: EntityType,
    text: str,
    normalized_name: Optional[str] = None,
    confidence: Optional[float] = None,
    start_pos: Optional[int] = None,
    end_pos: Optional[int] = None
) -> ClinicalEntity:
    entity = ClinicalEntity(
        document_id=document_id,
        entity_type=entity_type,
        text=text,
        normalized_name=normalized_name,
        confidence=confidence,
        start_pos=start_pos,
        end_pos=end_pos
    )
    db.add(entity)
    await db.flush()
    await db.refresh(entity)
    return entity


async def get_entities_for_document(db: AsyncSession, document_id: int) -> List[ClinicalEntity]:
    result = await db.execute(
        select(ClinicalEntity).where(ClinicalEntity.document_id == document_id)
    )
    return result.scalars().all()


async def create_code_mapping(
    db: AsyncSession,
    entity_id: int,
    code_system: str,
    code: str,
    name: Optional[str] = None,
    confidence: Optional[float] = None
) -> CodeMapping:
    mapping = CodeMapping(
        entity_id=entity_id,
        code_system=code_system,
        code=code,
        name=name,
        confidence=confidence
    )
    db.add(mapping)
    await db.flush()
    await db.refresh(mapping)
    return mapping


async def get_code_mappings_for_entity(db: AsyncSession, entity_id: int) -> List[CodeMapping]:
    result = await db.execute(
        select(CodeMapping).where(CodeMapping.entity_id == entity_id)
    )
    return result.scalars().all()
