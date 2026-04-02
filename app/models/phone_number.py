"""PhoneNumber model — voice reception bot."""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    number = Column(String, nullable=False, unique=True)  # E.164 format
    provider = Column(String, nullable=False)  # 'telnyx' or 'livekit'
    telnyx_connection_id = Column(String, nullable=True)
    livekit_dispatch_rule_id = Column(String, nullable=True)
    sms_enabled = Column(Boolean, nullable=False, default=False)

    agent = relationship("Agent", back_populates="phone_numbers")
