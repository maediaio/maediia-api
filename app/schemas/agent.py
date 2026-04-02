"""Agent schemas."""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel


class AgentCreate(BaseModel):
    name: str
    instructions: Optional[str] = None
    voice: str = "Ara"
    greeting: Optional[str] = None
    tools: Optional[Dict[str, Any]] = None
    post_call_rules: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    instructions: Optional[str] = None
    voice: Optional[str] = None
    greeting: Optional[str] = None
    is_active: Optional[bool] = None
    tools: Optional[Dict[str, Any]] = None
    post_call_rules: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    instructions: Optional[str] = None
    voice: str
    collection_id: Optional[str] = None
    greeting: Optional[str] = None
    is_active: bool
    tools: Optional[Dict[str, Any]] = None
    post_call_rules: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
