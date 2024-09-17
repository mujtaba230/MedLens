from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_doctor_or_admin, get_current_user
from app.models.user import User
from app.models.entity import EntityType
from app.models.document import ProcessingStatus
from app.crud.document import get_document, update_document_status
from app.crud.entity import create_clinical_entity, get_entities_for_document, create_code_mapping
from app.schemas.entity import ExtractedEntitiesResponse, CodeMappingSchema
from app.services.extraction_service import extraction_service
from app.services.code_mapping_service import code_mapping_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.post("/extract/{doc_id}", response_model=ExtractedEntitiesResponse)
async def extract_entities(
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

    if not doc.processed_text:
        raise HTTPException(status_code=400, detail="Document has no processed text. Run process first.")

    await update_document_status(db, doc_id, ProcessingStatus.EXTRACTING)
    raw_entities = await extraction_service.extract_entities(doc.processed_text)

    for re in raw_entities:
        try:
            et = EntityType(re.get("entity_type", "symptom").lower())
        except ValueError:
            et = EntityType.SYMPTOM
        entity = await create_clinical_entity(
            db,
            document_id=doc_id,
            entity_type=et,
            text=re.get("text", ""),
            normalized_name=re.get("normalized_name") or re.get("text", ""),
            confidence=re.get("confidence", 0.5)
        )

        # Auto-map codes
        codes = code_mapping_service.map_entity(entity.normalized_name, entity.entity_type.value)
        for code in codes:
            await create_code_mapping(
                db,
                entity_id=entity.id,
                code_system=code["code_system"],
                code=code["code"],
                name=code.get("name"),
                confidence=code.get("confidence", 0.5)
            )

    await update_document_status(db, doc_id, ProcessingStatus.MAPPING)

    await audit_service.log_action(
        db, current_user, "EXTRACT",
        resource_type="document", resource_id=doc_id,
        details={"entity_count": len(raw_entities)},
        request=request
    )

    entities = await get_entities_for_document(db, doc_id)
    return {"document_id": doc_id, "entities": entities}


@router.get("/{entity_id}/codes", response_model=List[CodeMappingSchema])
async def get_entity_codes(
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.crud.entity import get_code_mappings_for_entity
    codes = await get_code_mappings_for_entity(db, entity_id)
    return codes


@router.get("/{doc_id}", response_model=ExtractedEntitiesResponse)
async def get_entities(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = await get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role.value != "admin" and doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    entities = await get_entities_for_document(db, doc_id)
    return {"document_id": doc_id, "entities": entities}
