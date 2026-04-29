"""
MedBotX - FastAPI Application Entry Point
Developed by Bhaskar Shivaji Kumbhar
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="MedBotX - Advanced Medical Chatbot with Memory",
        description=(
            "An AI-powered healthcare chatbot with contextual memory, "
            "built with LangChain and OpenAI GPT-4o.\n\n"
            "**Developed by Bhaskar Shivaji Kumbhar**"
        ),
        version="1.0.0",
        contact={
            "name": "Bhaskar Shivaji Kumbhar",
        },
        license_info={"name": "MIT"},
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ──────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(api_router)

    # ── Global Exception Handler ────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal error occurred. Please try again.",
                "app": settings.APP_NAME,
                "developer": settings.DEVELOPER,
            },
        )

    return app


app = create_app()
