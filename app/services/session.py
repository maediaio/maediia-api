"""Session service — Redis-backed HTTP session management."""
from uuid import UUID
from app.services.redis import get_client

SESSION_PREFIX = "session:"
SESSION_TTL = 7 * 24 * 60 * 60  # 7 days in seconds


def _key(token: str) -> str:
    return f"{SESSION_PREFIX}{token}"


async def create(token: str, user_id: UUID) -> None:
    """Store a session token mapped to user_id with a 7-day TTL."""
    client = get_client()
    await client.set(_key(token), str(user_id), ex=SESSION_TTL)


async def get_user_id(token: str) -> str | None:
    """Return user_id string for a valid session token, or None if not found/expired."""
    client = get_client()
    return await client.get(_key(token))


async def delete(token: str) -> None:
    """Delete a session token from Redis (logout)."""
    client = get_client()
    await client.delete(_key(token))


async def refresh(token: str) -> None:
    """Reset the TTL on an existing session (sliding expiry)."""
    client = get_client()
    await client.expire(_key(token), SESSION_TTL)
