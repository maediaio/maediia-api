"""Organization schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    compliance_tier: Optional[str] = None
    sms_enabled: Optional[bool] = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    plan: str
    compliance_tier: str
    sms_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
