"""Voicemail schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class VoicemailResponse(BaseModel):
    id: UUID
    org_id: UUID
    business_line_id: UUID
    caller_number: Optional[str] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_read: bool
    called_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
