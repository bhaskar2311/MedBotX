"""
MedBotX - API Router Aggregator
Developed by Bhaskar Shivaji Kumbhar
"""
from fastapi import APIRouter
from app.api.routes import auth, chat, memory, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(memory.router)
