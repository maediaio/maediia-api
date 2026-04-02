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

    users = relationship("User", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")
    call_logs = relationship("CallLog", back_populates="organization")
    leads = relationship("Lead", back_populates="organization")
    services = relationship("Service", back_populates="organization")
    appointments = relationship("Appointment", back_populates="organization")
    business_lines = relationship("BusinessLine", back_populates="organization")
    api_keys = relationship("ApiKey", back_populates="organization")
    sms_logs = relationship("SmsLog", back_populates="organization")
    scheduled_tasks = relationship("ScheduledTask", back_populates="organization")
    voicemails = relationship("Voicemail", back_populates="organization")
