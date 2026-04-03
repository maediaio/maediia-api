"""SmsLog model — tracks post-call SMS sent via Telnyx."""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import ReadOnlyBase


class SmsLog(ReadOnlyBase):
    __tablename__ = "sms_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    call_log_id = Column(UUID(as_uuid=True), ForeignKey("call_logs.id"), nullable=True)
    to_number = Column(String, nullable=False)
    from_number = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    telnyx_message_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="queued")  # queued, sent, delivered, failed
    opt_out_checked = Column(Boolean, nullable=False, default=False)

    organization = relationship("Organization", backref="sms_logs")
    call_log = relationship("CallLog", backref="sms_logs")
