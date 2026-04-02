"""CallLog model — voice reception bot."""
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import ReadOnlyBase


class CallLog(ReadOnlyBase):
    __tablename__ = "call_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    direction = Column(String, nullable=False)  # 'inbound' or 'outbound'
    caller_number = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    outcome = Column(String, nullable=True)  # booked, callback, info_sent, etc.
    metadata_ = Column("metadata", JSONB, nullable=True)
    cost_cents = Column(Integer, nullable=True)

    organization = relationship("Organization", back_populates="call_logs")
    agent = relationship("Agent", back_populates="call_logs")
    sms_logs = relationship("SmsLog", back_populates="call_log")
