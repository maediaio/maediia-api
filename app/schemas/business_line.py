"""Business line schemas."""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel


class BusinessLineProvisionRequest(BaseModel):
    number: str  # E.164, selected from Telnyx search
    forward_to: Optional[str] = None
    forwarding_enabled: bool = True
    business_hours: Optional[Dict[str, Any]] = None
    whisper_enabled: bool = True
    voicemail_enabled: bool = True
    spam_filter_enabled: bool = True


class BusinessLineUpdate(BaseModel):
    forward_to: Optional[str] = None
    forwarding_enabled: Optional[bool] = None
    business_hours: Optional[Dict[str, Any]] = None
    whisper_enabled: Optional[bool] = None
    voicemail_enabled: Optional[bool] = None
    spam_filter_enabled: Optional[bool] = None


class BusinessLineResponse(BaseModel):
    id: UUID
    org_id: UUID
    telnyx_number_id: Optional[str] = None
    number: str
    forward_to: Optional[str] = None
    forwarding_enabled: bool
    business_hours: Optional[Dict[str, Any]] = None
    whisper_enabled: bool
    voicemail_enabled: bool
    spam_filter_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
