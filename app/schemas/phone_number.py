"""Phone number schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class PhoneNumberSearchRequest(BaseModel):
    country_code: str = "US"
    area_code: Optional[str] = None
    limit: int = 10


class PhoneNumberProvisionRequest(BaseModel):
    agent_id: UUID
    number: str  # E.164, selected from search results
    provider: str = "telnyx"
    sms_enabled: bool = False


class PhoneNumberResponse(BaseModel):
    id: UUID
    agent_id: UUID
    number: str
    provider: str
    telnyx_connection_id: Optional[str] = None
    livekit_dispatch_rule_id: Optional[str] = None
    sms_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}
