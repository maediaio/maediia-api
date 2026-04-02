"""Security utilities — session cookies and API key authentication."""
import secrets
import hashlib
from datetime import datetime
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_hex(32)


def generate_api_key() -> tuple[str, str]:
    """
    Generate an API key and its hash.
    Returns (raw_key, hashed_key).
    Raw key is shown to user once. Hashed key stored in DB.
    """
    raw_key = "mk_" + secrets.token_hex(32)
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, hashed_key


def hash_api_key(raw_key: str) -> str:
    """Hash an API key for storage or lookup."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Session cookie authentication for dashboard users.
    Reads session token from HTTP-only cookie.
    Validates against Redis session store.
    """
    from app.models.user import User

    session_token = request.cookies.get("session")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Look up session in Redis
    # redis_client.get(f"session:{session_token}") -> user_id
    # Placeholder until Redis session service is implemented
    user_id = await get_user_id_from_session(session_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid")

    # Load user from DB
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
):
    """
    API key authentication for service-to-service calls.
    Used by LiveKit agent workers to load agent config.
    Reads X-API-Key header, hashes it, looks up in DB.
    """
    from app.models.api_key import ApiKey

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    hashed = hash_api_key(api_key)

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_hash == hashed,
            ApiKey.is_active == True
        )
    )
    api_key_record = result.scalar_one_or_none()

    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key_record


async def get_user_id_from_session(session_token: str) -> Optional[str]:
    """Look up user_id from session token in Redis."""
    from app.services import session as session_service
    return await session_service.get_user_id(session_token)


def require_roles(*roles: str):
    """
    Role-based permission dependency factory.
    Usage: Depends(require_roles("admin", "sales"))
    """
    async def check_role(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Requires one of roles: {', '.join(roles)}"
            )
        return current_user
    return check_role
