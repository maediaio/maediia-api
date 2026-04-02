"""Main API router — registers all route modules."""
from fastapi import APIRouter

api_router = APIRouter()

# Routers registered here as they are built in Phase 0
# from app.api.routers import auth, organizations, agents, phone_numbers, knowledge_base, call_logs, webhooks
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
# api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
# api_router.include_router(phone_numbers.router, prefix="/phone-numbers", tags=["phone-numbers"])
# api_router.include_router(knowledge_base.router, prefix="/knowledge-base", tags=["knowledge-base"])
# api_router.include_router(call_logs.router, prefix="/calls", tags=["call-logs"])
# api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
