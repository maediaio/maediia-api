"""Call log schemas."""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel


class CallLogResponse(BaseModel):
    id: UUID
    org_id: UUID
    agent_id: UUID
    direction: str
    caller_number: Optional[str] = None
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    outcome: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None
    cost_cents: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
