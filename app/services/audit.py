"""Audit logging service — records all write operations."""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def audit_log(
    db: AsyncSession,
    action: str,
    resource_type: str,
    org_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    api_key_id: Optional[UUID] = None,
    resource_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    Add an audit log entry to the current DB session.
    The entry is committed with the calling endpoint's transaction.
    For HIPAA-tier orgs, also covers read operations (called explicitly from GET endpoints).
    """
    entry = AuditLog(
        org_id=org_id,
        user_id=user_id,
        api_key_id=api_key_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=ip_address,
    )
    db.add(entry)
