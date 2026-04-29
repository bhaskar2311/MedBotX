"""
MedBotX - Memory Manager (Temporary & Permanent)
Developed by Bhaskar Shivaji Kumbhar

Handles:
  - Temporary (in-process dict) memory per session
  - Permanent (DB-backed) memory per registered user
  - Optional Redis-backed session cache
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.models import MemoryRecord

logger = get_logger("memory_manager")

# In-process temporary memory: { session_id: [{"role": ..., "content": ..., "ts": ...}] }
_temp_store: Dict[str, List[Dict[str, Any]]] = {}


# ── Temporary (Session) Memory ────────────────────────────────────────────────

def create_session() -> str:
    session_id = str(uuid.uuid4())
    _temp_store[session_id] = []
    logger.debug(f"New session created: {session_id}")
    return session_id


def get_temp_memory(session_id: str) -> List[Dict[str, Any]]:
    return _temp_store.get(session_id, [])


def add_to_temp_memory(session_id: str, role: str, content: str) -> None:
    if session_id not in _temp_store:
        _temp_store[session_id] = []
    _temp_store[session_id].append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    # Trim to configured max
    max_msgs = settings.MAX_MEMORY_MESSAGES
    if len(_temp_store[session_id]) > max_msgs:
        _temp_store[session_id] = _temp_store[session_id][-max_msgs:]


def clear_temp_memory(session_id: str) -> None:
    _temp_store.pop(session_id, None)
    logger.debug(f"Session memory cleared: {session_id}")


def list_sessions() -> List[str]:
    return list(_temp_store.keys())


# ── Permanent (DB-backed) Memory ──────────────────────────────────────────────

async def load_permanent_memory(user_id: str, db: AsyncSession) -> Optional[MemoryRecord]:
    result = await db.execute(
        select(MemoryRecord).where(MemoryRecord.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def save_permanent_memory(
    user_id: str,
    history: List[Dict[str, Any]],
    db: AsyncSession,
    medical_context: Optional[Dict[str, Any]] = None,
    preferences: Optional[Dict[str, Any]] = None,
) -> MemoryRecord:
    record = await load_permanent_memory(user_id, db)

    # Keep only last MAX_MEMORY_MESSAGES for permanent store
    trimmed = history[-settings.MAX_MEMORY_MESSAGES:]

    if record is None:
        record = MemoryRecord(
            user_id=user_id,
            conversation_history=trimmed,
            medical_context=medical_context or {},
            preferences=preferences or {},
        )
        db.add(record)
    else:
        record.conversation_history = trimmed
        if medical_context is not None:
            record.medical_context = {**record.medical_context, **medical_context}
        if preferences is not None:
            record.preferences = {**record.preferences, **preferences}
        record.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)
    logger.info(f"Permanent memory saved for user: {user_id}")
    return record


async def update_medical_context(
    user_id: str, context_patch: Dict[str, Any], db: AsyncSession
) -> MemoryRecord:
    record = await load_permanent_memory(user_id, db)
    if record is None:
        record = MemoryRecord(
            user_id=user_id,
            conversation_history=[],
            medical_context=context_patch,
            preferences={},
        )
        db.add(record)
    else:
        record.medical_context = {**record.medical_context, **context_patch}
        record.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)
    return record


async def delete_permanent_memory(user_id: str, db: AsyncSession) -> bool:
    record = await load_permanent_memory(user_id, db)
    if record:
        await db.delete(record)
        await db.commit()
        logger.info(f"Permanent memory deleted for user: {user_id}")
        return True
    return False


def merge_memories(
    permanent: Optional[MemoryRecord],
    temp: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Merge permanent history with current session for context window."""
    base: List[Dict[str, Any]] = []
    if permanent and permanent.conversation_history:
        base = list(permanent.conversation_history)
    merged = base + temp
    return merged[-settings.MAX_MEMORY_MESSAGES:]
