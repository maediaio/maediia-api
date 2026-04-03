"""Organization model — shared across all bots."""
import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    plan = Column(String, nullable=False, default="starter")
    compliance_tier = Column(String, nullable=False, default="standard")  # 'standard' or 'hipaa'
    sms_enabled = Column(Boolean, nullable=False, default=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # Note: All backrefs defined on child model sides to avoid circular imports
