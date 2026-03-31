"""Main API router."""
from fastapi import APIRouter

# Import sub-routers as they're created
# from app.api.v1 import auth, users, voice

api_router = APIRouter()

# Register sub-routers
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
