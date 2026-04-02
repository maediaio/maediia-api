"""Phone numbers router — Telnyx number provisioning."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.agent import Agent
from app.models.phone_number import PhoneNumber
from app.models.user import User
from app.schemas.phone_number import (
    PhoneNumberProvisionRequest,
    PhoneNumberResponse,
    PhoneNumberSearchRequest,
)
from app.services.audit import audit_log

router = APIRouter()


@router.post("/phone-numbers/search")
async def search_phone_numbers(
    payload: PhoneNumberSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search available numbers via Telnyx. Implemented in Phase 0 Step 5."""
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # TODO: call Telnyx Numbers API to search available numbers
    raise HTTPException(status_code=501, detail="Telnyx number search not yet implemented")


@router.post("/phone-numbers/provision", response_model=PhoneNumberResponse, status_code=201)
async def provision_phone_number(
    payload: PhoneNumberProvisionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Buy number + configure Telnyx SIP trunk + create dispatch rule + save to DB."""
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Verify the agent belongs to user's org
    agent_result = await db.execute(
        select(Agent).where(
            Agent.id == payload.agent_id,
            Agent.org_id == current_user.org_id,
        )
    )
    if not agent_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent not found")

    # TODO: purchase number from Telnyx, create SIP trunk connection, create LiveKit dispatch rule
    # telnyx_connection_id = await telnyx_service.provision_number(payload.number)
    # livekit_dispatch_rule_id = await livekit_service.create_dispatch_rule(agent_id)

    phone = PhoneNumber(
        agent_id=payload.agent_id,
        number=payload.number,
        provider=payload.provider,
        sms_enabled=payload.sms_enabled,
        # telnyx_connection_id and livekit_dispatch_rule_id set after external calls above
    )
    db.add(phone)

    await audit_log(
        db,
        action="created",
        resource_type="phone_number",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=phone.id,
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(phone)
    return phone


@router.delete("/phone-numbers/{phone_number_id}", status_code=204)
async def delete_phone_number(
    phone_number_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Verify ownership via agent → org
    result = await db.execute(
        select(PhoneNumber)
        .join(Agent, PhoneNumber.agent_id == Agent.id)
        .where(
            PhoneNumber.id == phone_number_id,
            Agent.org_id == current_user.org_id,
        )
    )
    phone = result.scalar_one_or_none()
    if not phone:
        raise HTTPException(status_code=404, detail="Phone number not found")

    # TODO: release number from Telnyx, remove dispatch rule from LiveKit

    await audit_log(
        db,
        action="deleted",
        resource_type="phone_number",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=phone_number_id,
        ip_address=request.client.host if request.client else None,
    )

    await db.delete(phone)
    await db.commit()


@router.get("/agents/{agent_id}/phone-numbers", response_model=List[PhoneNumberResponse])
async def list_agent_phone_numbers(
    agent_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify agent belongs to user's org
    agent_result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.org_id == current_user.org_id,
        )
    )
    if not agent_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent not found")

    result = await db.execute(
        select(PhoneNumber).where(PhoneNumber.agent_id == agent_id)
    )
    return result.scalars().all()
