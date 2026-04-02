"""Agents router — voice reception agent CRUD."""
from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_api_key, get_current_user
from app.db.session import get_db
from app.models.agent import Agent
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.schemas import PaginatedResponse
from app.services.audit import audit_log

router = APIRouter()

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def _get_principal(
    request: Request,
    db: AsyncSession = Depends(get_db),
    raw_api_key: Optional[str] = Security(_api_key_header),
) -> Union[User, ApiKey]:
    """Accept either session cookie (dashboard) or API key (agent workers)."""
    session_token = request.cookies.get("session")
    if session_token:
        return await get_current_user(request, db)
    if raw_api_key:
        return await get_api_key(raw_api_key, db)
    raise HTTPException(status_code=401, detail="Authentication required")


@router.post("/agents", response_model=AgentResponse, status_code=201)
async def create_agent(
    payload: AgentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    agent = Agent(org_id=current_user.org_id, **payload.model_dump())
    db.add(agent)

    await audit_log(
        db,
        action="created",
        resource_type="agent",
        org_id=current_user.org_id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(agent)
    return agent


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    principal: Union[User, ApiKey] = Depends(_get_principal),
    db: AsyncSession = Depends(get_db),
):
    org_id = principal.org_id

    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    payload: AgentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == current_user.org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)

    await audit_log(
        db,
        action="updated",
        resource_type="agent",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=agent_id,
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(agent)
    return agent


@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == current_user.org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await audit_log(
        db,
        action="deleted",
        resource_type="agent",
        org_id=current_user.org_id,
        user_id=current_user.id,
        resource_id=agent_id,
        ip_address=request.client.host if request.client else None,
    )

    await db.delete(agent)
    await db.commit()


@router.get("/organizations/{org_id}/agents", response_model=List[AgentResponse])
async def list_org_agents(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin" and current_user.org_id != org_id:
        raise HTTPException(status_code=404, detail="Organization not found")

    result = await db.execute(
        select(Agent).where(Agent.org_id == org_id)
    )
    return result.scalars().all()
