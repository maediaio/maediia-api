"""FastAPI application factory."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router
from app.services import redis as redis_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    await redis_service.connect()
    yield
    await redis_service.disconnect()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="MAEDIIA Platform API — api.maediia.com",
        version="1.0.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes — no versioning prefix
    app.include_router(api_router)

    # Health check
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": settings.APP_NAME}

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "docs": "/docs",
        }

    return app


app = create_app()
