"""
MedBotX - Memory Routes
Developed by Bhaskar Shivaji Kumbhar
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.models import User
from app.memory import memory_manager
from app.models.schemas import (
    MedicalContextUpdateRequest,
    MemoryLoadResponse,
    MemorySaveRequest,
)

router = APIRouter(prefix="/memory", tags=["Memory"])
logger = get_logger("memory_routes")


@router.get("/load", response_model=MemoryLoadResponse)
async def load_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Load the authenticated user's permanent memory."""
    record = await memory_manager.load_permanent_memory(current_user.id, db)
    if record is None:
        return MemoryLoadResponse(
            user_id=current_user.id,
            conversation_history=[],
            medical_context={},
            preferences={},
        )
    return MemoryLoadResponse(
        user_id=current_user.id,
        conversation_history=record.conversation_history or [],
        medical_context=record.medical_context or {},
        preferences=record.preferences or {},
        updated_at=record.updated_at,
    )


@router.post("/save", status_code=status.HTTP_200_OK)
async def save_memory(
    payload: MemorySaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually save/update the user's permanent memory."""
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    history = payload.data.get("conversation_history", [])
    medical_context = payload.data.get("medical_context")
    preferences = payload.data.get("preferences")

    await memory_manager.save_permanent_memory(
        user_id=current_user.id,
        history=history,
        db=db,
        medical_context=medical_context,
        preferences=preferences,
    )
    return {"status": "success", "user_id": current_user.id}


@router.put("/medical-context", status_code=status.HTTP_200_OK)
async def update_medical_context(
    payload: MedicalContextUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the user's stored medical context (allergies, conditions, medications)."""
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    context_patch = {}
    if payload.allergies is not None:
        context_patch["allergies"] = payload.allergies
    if payload.conditions is not None:
        context_patch["conditions"] = payload.conditions
    if payload.medications is not None:
        context_patch["medications"] = payload.medications
    if payload.age is not None:
        context_patch["age"] = payload.age
    if payload.blood_type is not None:
        context_patch["blood_type"] = payload.blood_type
    if payload.notes is not None:
        context_patch["notes"] = payload.notes

    record = await memory_manager.update_medical_context(current_user.id, context_patch, db)
    return {"status": "success", "medical_context": record.medical_context}


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_permanent_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete the authenticated user's permanent memory."""
    await memory_manager.delete_permanent_memory(current_user.id, db)
