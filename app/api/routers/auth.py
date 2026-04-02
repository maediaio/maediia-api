"""Auth router — login, logout, session, API key management."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    generate_api_key,
    generate_session_token,
    get_current_user,
    hash_api_key,
    verify_password,
)
from app.db.session import get_db
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.auth import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    LoginRequest,
    UserResponse,
)
from app.services.audit import audit_log

router = APIRouter()

SESSION_COOKIE = "session"
SESSION_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


@router.post("/auth/login", response_model=UserResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = generate_session_token()

    # Store session in Redis — implemented in Phase 0 Step 3
    # await session_service.create(token, str(user.id))

    await audit_log(
        db,
        action="login",
        resource_type="session",
        org_id=user.org_id,
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )

    return user


@router.post("/auth/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Delete session from Redis — implemented in Phase 0 Step 3
    # await session_service.delete(session_token)

    await audit_log(
        db,
        action="logout",
        resource_type="session",
        org_id=current_user.org_id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    response.delete_cookie(key=SESSION_COOKIE)


@router.get("/auth/session", response_model=UserResponse)
async def get_session(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/auth/api-keys", response_model=ApiKeyCreatedResponse, status_code=201)
async def create_api_key(
    payload: ApiKeyCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    raw_key, hashed_key = generate_api_key()

    key_record = ApiKey(
        org_id=current_user.org_id,
        name=payload.name,
        key_hash=hashed_key,
    )
    db.add(key_record)

    await audit_log(
        db,
        action="created",
        resource_type="api_key",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=key_record.id,
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(key_record)

    return ApiKeyCreatedResponse(
        id=key_record.id,
        org_id=key_record.org_id,
        name=key_record.name,
        is_active=key_record.is_active,
        created_at=key_record.created_at,
        key=raw_key,
    )


@router.get("/auth/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.org_id == current_user.org_id,
            ApiKey.is_active == True,
        )
    )
    return result.scalars().all()
