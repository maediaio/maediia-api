"""Service model — shared across all bots."""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    price_cents = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    organization = relationship("Organization", backref="services")
    appointments = relationship("Appointment", back_populates="service")
