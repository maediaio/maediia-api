"""AuditLog model — append-only record of all write operations."""
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=True)   # null for cross-org admin ops
    user_id = Column(UUID(as_uuid=True), nullable=True)  # null for API key auth
    api_key_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String, nullable=False)              # created, updated, deleted, accessed
    resource_type = Column(String, nullable=False)       # agent, phone_number, etc.
    resource_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    # created_at inherited from Base; updated_at present but never changes (immutable log)
