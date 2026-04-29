"""
MedBotX - Pydantic Schemas (API Request/Response Models)
Developed by Bhaskar Shivaji Kumbhar
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Chat Schemas ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 4000:
            raise ValueError("Message too long (max 4000 chars)")
        return v


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    model: str
    tokens_used: Optional[int] = None


class MessageItem(BaseModel):
    role: str
    content: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]
    total_messages: int


# ── Memory Schemas ────────────────────────────────────────────────────────────

class MemorySaveRequest(BaseModel):
    user_id: str
    data: Dict[str, Any]


class MemoryLoadResponse(BaseModel):
    user_id: str
    conversation_history: List[Dict[str, Any]]
    medical_context: Dict[str, Any]
    preferences: Dict[str, Any]
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MedicalContextUpdateRequest(BaseModel):
    user_id: Optional[str] = None   # optional – backend uses JWT user if omitted
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    age: Optional[int] = None
    blood_type: Optional[str] = None
    notes: Optional[str] = None


# ── Health / Status Schemas ───────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    developer: str
    environment: str
    timestamp: datetime
