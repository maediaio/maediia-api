"""Lead model — shared across all bots."""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    source = Column(String, nullable=True)
    status = Column(String, nullable=True)
    sms_opt_out = Column(Boolean, nullable=False, default=False)  # REQUIRED for compliance

    organization = relationship("Organization", backref="leads")
    appointments = relationship("Appointment", back_populates="lead")
