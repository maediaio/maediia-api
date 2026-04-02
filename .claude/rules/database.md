# Database Rules

> Reference these rules before creating or modifying any database models or migrations.

---

## Schema Reference

Full schema with all tables and columns: @docs/PLATFORM_ARCHITECTURE.md Section 3

---

## Primary Keys

ALL primary keys must be UUID:

id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

Never use integer auto-increment PKs.

---

## Timestamps

ALL tables must have created_at:

created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

ALL mutable tables must also have updated_at:

updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

Read-only tables (logs, audit records) only need created_at.

---

## Foreign Keys

Non-nullable FK:
org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

Nullable FK:
service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=True)

Always specify nullable explicitly. Never rely on defaults.

---

## JSONB Columns

Use PostgreSQL JSONB for flexible structured data:
from sqlalchemy.dialects.postgresql import JSONB

tools = Column(JSONB, nullable=True)
post_call_rules = Column(JSONB, nullable=True)
metadata = Column(JSONB, nullable=True)

Never use JSON (use JSONB — it's indexed and faster).

---

## Relationships

Always define back_populates on both sides:

In Organization model:
agents = relationship("Agent", back_populates="organization")

In Agent model:
organization = relationship("Organization", back_populates="agents")

---

## Model File Structure

One model per file in app/models/
All models imported in app/models/__init__.py

app/models/__init__.py should import:
from app.models.organization import Organization
from app.models.user import User
from app.models.agent import Agent
from app.models.phone_number import PhoneNumber
from app.models.call_log import CallLog
from app.models.sms_log import SmsLog
from app.models.scheduled_task import ScheduledTask
from app.models.lead import Lead
from app.models.service import Service
from app.models.appointment import Appointment

---

## Async Database Operations

Database URL must use asyncpg driver:
postgresql+asyncpg://user:password@host/dbname

Always use AsyncSession:
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

Single result:
result = await db.execute(
    select(Agent).where(Agent.id == agent_id, Agent.org_id == org_id)
)
agent = result.scalar_one_or_none()

Multiple results:
result = await db.execute(
    select(Agent).where(Agent.org_id == org_id)
)
agents = result.scalars().all()

Create:
db.add(new_agent)
await db.commit()
await db.refresh(new_agent)
return new_agent

Delete:
await db.delete(agent)
await db.commit()

Never use synchronous query() — always use async select().

---

## Tenant Isolation

EVERY org-scoped query MUST filter by org_id.
This is non-negotiable. Missing org_id filter = data leak between clients.

CORRECT:
select(Agent).where(Agent.id == agent_id, Agent.org_id == current_user.org_id)

WRONG — never do this:
select(Agent).where(Agent.id == agent_id)

Only Admin role can query across org boundaries, and only on admin-specific endpoints.

---

## Alembic Migrations

Migrations are APPEND-ONLY — never modify existing migration files.
Always create new migration for any schema change.
Test up AND down before committing.
Use descriptive names: "add_sms_opt_out_to_leads", "add_updated_at_to_call_logs"

Create migration:
alembic revision --autogenerate -m "add_sms_opt_out_to_leads"

Apply:
alembic upgrade head

Rollback one:
alembic downgrade -1

---

## Required Columns by Table Type

All tables:
- id (UUID PK)
- created_at (TIMESTAMP)

Mutable tables (anything that can be edited):
- updated_at (TIMESTAMP with onupdate)

Org-scoped tables:
- org_id (UUID FK to organizations.id, nullable=False)

SMS/outreach tables:
- sms_opt_out (BOOLEAN, default=False) — REQUIRED for compliance

---

## Compliance Notes

- Transcripts in call_logs encrypted at rest for hipaa-tier orgs
- All PHI fields must be noted in model docstring
- Never log PHI to application logs
- Audit log every access to call_logs, transcripts for hipaa-tier orgs
