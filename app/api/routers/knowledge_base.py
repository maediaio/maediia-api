"""Knowledge base router — xAI Collections management. Implemented in Part 2."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.agent import Agent
from app.models.user import User

router = APIRouter()


async def _get_agent_for_org(agent_id: UUID, org_id: UUID, db: AsyncSession) -> Agent:
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/agents/{agent_id}/knowledge-base", status_code=201)
async def upload_knowledge_base_document(
    agent_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document to the agent's xAI Collection. Implemented in Part 2."""
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    await _get_agent_for_org(agent_id, current_user.org_id, db)

    # TODO Part 2: create xAI Collection if none exists, upload document
    raise HTTPException(status_code=501, detail="Knowledge base not yet implemented — see Part 2")


@router.get("/agents/{agent_id}/knowledge-base")
async def list_knowledge_base_documents(
    agent_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List documents in the agent's xAI Collection. Implemented in Part 2."""
    await _get_agent_for_org(agent_id, current_user.org_id, db)

    # TODO Part 2: fetch document list from xAI Collections API
    raise HTTPException(status_code=501, detail="Knowledge base not yet implemented — see Part 2")


@router.delete("/agents/{agent_id}/knowledge-base/{doc_id}", status_code=204)
async def delete_knowledge_base_document(
    agent_id: UUID,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document from the agent's xAI Collection. Implemented in Part 2."""
    if current_user.role not in ("admin",):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    await _get_agent_for_org(agent_id, current_user.org_id, db)

    # TODO Part 2: delete document from xAI Collections API
    raise HTTPException(status_code=501, detail="Knowledge base not yet implemented — see Part 2")
