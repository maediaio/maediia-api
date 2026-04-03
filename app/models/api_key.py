"""ApiKey model — service-to-service authentication."""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)  # descriptive label
    key_hash = Column(String, nullable=False, unique=True)  # SHA256 of raw key
    is_active = Column(Boolean, nullable=False, default=True)

    organization = relationship("Organization", backref="api_keys")
