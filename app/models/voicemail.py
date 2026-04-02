"""Voicemail model — append-only log of voicemails per business line."""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Voicemail(Base):
    __tablename__ = "voicemails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    business_line_id = Column(UUID(as_uuid=True), ForeignKey("business_lines.id"), nullable=False)
    caller_number = Column(String, nullable=True)
    recording_url = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    called_at = Column(DateTime(timezone=True), nullable=True)

    business_line = relationship("BusinessLine", back_populates="voicemails")
