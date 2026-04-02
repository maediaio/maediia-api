"""Call logs router — call history and transcripts."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.agent import Agent
from app.models.call_log import CallLog
from app.models.user import User
from app.schemas.call_log import CallLogResponse
from app.schemas import PaginatedResponse

router = APIRouter()


@router.get("/agents/{agent_id}/calls", response_model=PaginatedResponse[CallLogResponse])
async def list_agent_calls(
    agent_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
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

    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count()).where(
            CallLog.agent_id == agent_id,
            CallLog.org_id == current_user.org_id,
        )
    )
    total = total_result.scalar()

    result = await db.execute(
        select(CallLog)
        .where(CallLog.agent_id == agent_id, CallLog.org_id == current_user.org_id)
        .order_by(CallLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/calls/{call_id}", response_model=CallLogResponse)
async def get_call(
    call_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CallLog).where(
            CallLog.id == call_id,
            CallLog.org_id == current_user.org_id,
        )
    )
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call log not found")

    return call


@router.get("/organizations/{org_id}/calls", response_model=PaginatedResponse[CallLogResponse])
async def list_org_calls(
    org_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin" and current_user.org_id != org_id:
        raise HTTPException(status_code=404, detail="Organization not found")

    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count()).where(CallLog.org_id == org_id)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(CallLog)
        .where(CallLog.org_id == org_id)
        .order_by(CallLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)
