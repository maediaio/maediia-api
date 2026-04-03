"""ScheduledTask model — ARQ task queue persistence (shared by all bots)."""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    task_name = Column(String, nullable=False)  # ARQ function name
    args = Column(JSONB, nullable=True)
    kwargs = Column(JSONB, nullable=True)
    enqueue_at = Column(DateTime(timezone=True), nullable=True)  # None = immediate
    status = Column(String, nullable=False, default="pending")  # pending, running, complete, failed
    arq_job_id = Column(String, nullable=True)
    result = Column(JSONB, nullable=True)

    organization = relationship("Organization", backref="scheduled_tasks")
