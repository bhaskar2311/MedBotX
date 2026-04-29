"""
MedBotX - Health & Status Routes
Developed by Bhaskar Shivaji Kumbhar
"""
from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        app=settings.APP_NAME,
        version="1.0.0",
        developer=settings.DEVELOPER,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/")
async def root():
    return {
        "app": "MedBotX - Advanced Medical Chatbot with Memory",
        "developer": "Bhaskar Shivaji Kumbhar",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
    }
