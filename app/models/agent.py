"""Agent model — voice reception bot."""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    instructions = Column(Text, nullable=True)
    voice = Column(String, nullable=False, default="Ara")  # xAI voice: Ara, Rex, Sal, Eve, Leo
    collection_id = Column(String, nullable=True)  # xAI Collection ID
    tools = Column(JSONB, nullable=True)
    post_call_rules = Column(JSONB, nullable=True)
    greeting = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    organization = relationship("Organization", backref="agents")
    phone_numbers = relationship("PhoneNumber", back_populates="agent")
    # Note: backref defined on CallLog side
