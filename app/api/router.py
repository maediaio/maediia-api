"""Main API router — registers all route modules."""
from fastapi import APIRouter

from app.api.routers import (
    agents,
    auth,
    business_lines,
    call_logs,
    knowledge_base,
    organizations,
    phone_numbers,
    voicemails,
    webhooks,
)

api_router = APIRouter()

# Routers use full paths (flat routing, no versioning prefix)
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(organizations.router, tags=["organizations"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(phone_numbers.router, tags=["phone-numbers"])
api_router.include_router(knowledge_base.router, tags=["knowledge-base"])
api_router.include_router(call_logs.router, tags=["call-logs"])
api_router.include_router(webhooks.router, tags=["webhooks"])
api_router.include_router(business_lines.router, tags=["business-lines"])
api_router.include_router(voicemails.router, tags=["voicemails"])
