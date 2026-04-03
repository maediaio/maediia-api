"""BusinessLine model — call forwarding + voicemail feature."""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, backref

from app.db.base import Base


class BusinessLine(Base):
    __tablename__ = "business_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    telnyx_number_id = Column(String, nullable=True)
    number = Column(String, nullable=False, unique=True)  # E.164 format
    forward_to = Column(String, nullable=True)  # E.164 number to forward calls to
    forwarding_enabled = Column(Boolean, nullable=False, default=True)
    business_hours = Column(JSONB, nullable=True)
    whisper_enabled = Column(Boolean, nullable=False, default=True)
    voicemail_enabled = Column(Boolean, nullable=False, default=True)
    spam_filter_enabled = Column(Boolean, nullable=False, default=True)

    organization = relationship("Organization", backref="business_lines")
    # Note: backref defined on Voicemail side to avoid circular import
