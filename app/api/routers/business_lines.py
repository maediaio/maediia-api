"""Business lines router — virtual business line management."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.business_line import BusinessLine
from app.models.user import User
from app.models.voicemail import Voicemail
from app.schemas.business_line import (
    BusinessLineProvisionRequest,
    BusinessLineResponse,
    BusinessLineUpdate,
)
from app.schemas.voicemail import VoicemailResponse
from app.schemas import PaginatedResponse
from app.services.audit import audit_log

router = APIRouter()


@router.post("/business-lines/provision", response_model=BusinessLineResponse, status_code=201)
async def provision_business_line(
    payload: BusinessLineProvisionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Buy Telnyx number, configure forwarding/voicemail, save to DB."""
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Check number isn't already provisioned
    existing = await db.execute(
        select(BusinessLine).where(BusinessLine.number == payload.number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Number already provisioned")

    # TODO: purchase number from Telnyx, configure connection ID
    # telnyx_number_id = await telnyx_service.purchase_number(payload.number)

    line = BusinessLine(
        org_id=current_user.org_id,
        number=payload.number,
        forward_to=payload.forward_to,
        forwarding_enabled=payload.forwarding_enabled,
        business_hours=payload.business_hours,
        whisper_enabled=payload.whisper_enabled,
        voicemail_enabled=payload.voicemail_enabled,
        spam_filter_enabled=payload.spam_filter_enabled,
    )
    db.add(line)

    await audit_log(
        db,
        action="created",
        resource_type="business_line",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=line.id,
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(line)
    return line


@router.get("/business-lines/{line_id}", response_model=BusinessLineResponse)
async def get_business_line(
    line_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BusinessLine).where(
            BusinessLine.id == line_id,
            BusinessLine.org_id == current_user.org_id,
        )
    )
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(status_code=404, detail="Business line not found")

    return line


@router.put("/business-lines/{line_id}", response_model=BusinessLineResponse)
async def update_business_line(
    line_id: UUID,
    payload: BusinessLineUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(
        select(BusinessLine).where(
            BusinessLine.id == line_id,
            BusinessLine.org_id == current_user.org_id,
        )
    )
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(status_code=404, detail="Business line not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(line, field, value)

    await audit_log(
        db,
        action="updated",
        resource_type="business_line",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=line_id,
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(line)
    return line


@router.delete("/business-lines/{line_id}", status_code=204)
async def delete_business_line(
    line_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(
        select(BusinessLine).where(
            BusinessLine.id == line_id,
            BusinessLine.org_id == current_user.org_id,
        )
    )
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(status_code=404, detail="Business line not found")

    # TODO: release number from Telnyx

    await audit_log(
        db,
        action="deleted",
        resource_type="business_line",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=line_id,
        ip_address=request.client.host if request.client else None,
    )

    await db.delete(line)
    await db.commit()


@router.get("/organizations/{org_id}/business-lines", response_model=List[BusinessLineResponse])
async def list_org_business_lines(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin" and current_user.org_id != org_id:
        raise HTTPException(status_code=404, detail="Organization not found")

    result = await db.execute(
        select(BusinessLine).where(BusinessLine.org_id == org_id)
    )
    return result.scalars().all()


@router.get(
    "/business-lines/{line_id}/voicemails",
    response_model=PaginatedResponse[VoicemailResponse],
)
async def list_business_line_voicemails(
    line_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify business line belongs to user's org
    line_result = await db.execute(
        select(BusinessLine).where(
            BusinessLine.id == line_id,
            BusinessLine.org_id == current_user.org_id,
        )
    )
    if not line_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Business line not found")

    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count()).where(Voicemail.business_line_id == line_id)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(Voicemail)
        .where(Voicemail.business_line_id == line_id)
        .order_by(Voicemail.called_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)
