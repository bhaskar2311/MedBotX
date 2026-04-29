"""
MedBotX - Chat Routes
Developed by Bhaskar Shivaji Kumbhar
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_optional_user
from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.models import User
from app.memory import memory_manager
from app.models.schemas import ChatRequest, ChatResponse, SessionHistoryResponse, MessageItem
from app.services.chatbot_service import chatbot_service
from datetime import datetime, timezone

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_logger("chat_routes")


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to MedBotX and receive a context-aware medical response.

    - Anonymous users: get temporary session memory (cleared on session end)
    - Authenticated users: get permanent memory loaded from DB
    """
    session_id = payload.session_id
    if not session_id:
        session_id = memory_manager.create_session()

    # Validate or create session
    existing = memory_manager.get_temp_memory(session_id)
    if existing is None and not payload.session_id:
        memory_manager.create_session()

    # Load permanent memory for authenticated users
    permanent_memory = None
    if current_user:
        permanent_memory = await memory_manager.load_permanent_memory(current_user.id, db)

    result = await chatbot_service.get_response(
        user_message=payload.message,
        session_id=session_id,
        permanent_memory=permanent_memory,
    )

    # Persist memory for authenticated users after each turn
    if current_user:
        temp_history = memory_manager.get_temp_memory(session_id)
        await memory_manager.save_permanent_memory(
            user_id=current_user.id,
            history=temp_history,
            db=db,
        )

    return ChatResponse(**result)


@router.get("/history/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """Retrieve the conversation history for a session."""
    history = memory_manager.get_temp_memory(session_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )
    messages = [
        MessageItem(
            role=msg["role"],
            content=msg["content"],
            timestamp=datetime.fromisoformat(msg["timestamp"]),
        )
        for msg in history
    ]
    return SessionHistoryResponse(
        session_id=session_id,
        messages=messages,
        total_messages=len(messages),
    )


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_session(session_id: str):
    """Clear temporary session memory."""
    memory_manager.clear_temp_memory(session_id)


@router.post("/session/new")
async def new_session():
    """Create a new anonymous session."""
    session_id = memory_manager.create_session()
    return {"session_id": session_id}
