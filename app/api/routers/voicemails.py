"""Voicemails router."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.business_line import BusinessLine
from app.models.user import User
from app.models.voicemail import Voicemail
from app.schemas.voicemail import VoicemailResponse
from app.services.audit import audit_log

router = APIRouter()


@router.get("/voicemails/{voicemail_id}", response_model=VoicemailResponse)
async def get_voicemail(
    voicemail_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Voicemail).where(
            Voicemail.id == voicemail_id,
            Voicemail.org_id == current_user.org_id,
        )
    )
    voicemail = result.scalar_one_or_none()
    if not voicemail:
        raise HTTPException(status_code=404, detail="Voicemail not found")

    return voicemail


@router.put("/voicemails/{voicemail_id}/read", response_model=VoicemailResponse)
async def mark_voicemail_read(
    voicemail_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Voicemail).where(
            Voicemail.id == voicemail_id,
            Voicemail.org_id == current_user.org_id,
        )
    )
    voicemail = result.scalar_one_or_none()
    if not voicemail:
        raise HTTPException(status_code=404, detail="Voicemail not found")

    voicemail.is_read = True

    await audit_log(
        db,
        action="updated",
        resource_type="voicemail",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=voicemail_id,
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(voicemail)
    return voicemail
