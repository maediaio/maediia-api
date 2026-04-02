"""Auth schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    org_id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    user: UserResponse


class ApiKeyCreate(BaseModel):
    name: str


class ApiKeyResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Returned once on creation — includes the raw key."""
    key: str
