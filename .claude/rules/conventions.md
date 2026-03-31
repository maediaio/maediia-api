# MAEDIIA Build Conventions

> Every sub-agent MUST read this before writing any code. These rules are non-negotiable.

## Project Structure

```
maediia-api/
├── alembic/                 # DB migrations
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings from env vars
│   ├── database.py          # SQLAlchemy engine + session
│   ├── dependencies.py      # Shared FastAPI dependencies
│   ├── middleware/
│   │   ├── auth.py          # Session + API key validation
│   │   └── audit.py         # Audit logging middleware
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py      # Import all models here
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── service.py
│   │   ├── appointment.py
│   │   ├── lead.py
│   │   ├── bot_subscription.py
│   │   ├── billing.py
│   │   ├── message_log.py
│   │   ├── scheduled_task.py
│   │   ├── audit_log.py
│   │   ├── api_key.py
│   │   ├── notification_preference.py
│   │   ├── agent.py         # Voice bot
│   │   ├── phone_number.py  # Voice bot
│   │   └── call_log.py      # Voice bot
│   ├── schemas/             # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── user.py
│   │   └── ...              # Mirror models/ structure
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── organizations.py
│   │   ├── users.py
│   │   ├── customers.py
│   │   ├── services.py
│   │   ├── appointments.py
│   │   ├── leads.py
│   │   ├── billing.py
│   │   ├── bots.py
│   │   ├── messaging.py
│   │   ├── analytics.py
│   │   ├── admin.py
│   │   ├── webhooks.py      # All webhook handlers
│   │   ├── agents.py        # Voice bot
│   │   ├── phone_numbers.py # Voice bot
│   │   └── calls.py         # Voice bot
│   ├── services/            # Business logic (NOT FastAPI routes)
│   │   ├── stripe_service.py
│   │   ├── telnyx_service.py
│   │   ├── xai_service.py
│   │   ├── livekit_service.py
│   │   └── audit_service.py
│   └── tasks/               # ARQ background tasks
│       ├── __init__.py
│       ├── sms_tasks.py
│       ├── reminder_tasks.py
│       └── worker.py        # ARQ worker entry
├── tests/
│   ├── conftest.py          # Fixtures
│   ├── test_auth.py
│   ├── test_organizations.py
│   └── ...                  # Mirror routers/ structure
├── scripts/
│   ├── migrate_users.py     # JSON -> Postgres migration
│   └── seed.py              # Dev seed data
├── .env.example
├── alembic.ini
├── requirements.txt
├── Dockerfile               # Optional
└── README.md
```

## Naming Conventions

|Thing             |Convention                            |Example                                                           |
|------------------|--------------------------------------|------------------------------------------------------------------|
|DB tables         |snake_case, plural                    |`organizations`, `call_logs`, `bot_subscriptions`                 |
|DB columns        |snake_case                            |`org_id`, `created_at`, `stripe_customer_id`                      |
|SQLAlchemy models |PascalCase, singular                  |`Organization`, `CallLog`, `BotSubscription`                      |
|Pydantic schemas  |PascalCase + suffix                   |`OrganizationCreate`, `OrganizationResponse`, `OrganizationUpdate`|
|Routers           |snake_case, plural                    |`organizations.py`, `phone_numbers.py`                            |
|Router prefix     |`/resource`                           |`/organizations`, `/agents`, `/calls`                             |
|Service files     |snake_case + `_service`               |`stripe_service.py`, `telnyx_service.py`                          |
|Task files        |snake_case + `_tasks`                 |`sms_tasks.py`, `reminder_tasks.py`                               |
|Test files        |`test_` + module name                 |`test_organizations.py`, `test_auth.py`                           |
|Env vars          |UPPER_SNAKE_CASE                      |`DATABASE_URL`, `STRIPE_SECRET_KEY`                               |
|Alembic migrations|auto-generated timestamp + description|`2026_03_24_add_customers_table.py`                               |
|Git branches      |`feature/short-description`           |`feature/auth-middleware`, `feature/stripe-billing`               |
|Git commits       |imperative, lowercase                 |`add organization crud endpoints`, `fix auth session validation`  |

## SQLAlchemy Model Pattern

Every model MUST follow this exact structure:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    # ... all columns from schema ...
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    customers = relationship("Customer", back_populates="organization")
```

Rules:

- ALL primary keys are UUID, auto-generated with `uuid.uuid4`
- ALL foreign keys use `UUID(as_uuid=True)` type
- ALL tables have `created_at` (auto-set)
- ALL mutable tables have `updated_at` (auto-updated)
- ALL nullable FKs explicitly marked `nullable=True`
- JSONB columns use `JSONB` type from `sqlalchemy.dialects.postgresql`
- Relationships defined on both sides with `back_populates`

## Pydantic Schema Pattern

```python
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class OrganizationBase(BaseModel):
    name: str
    industry: Optional[str] = None
    timezone: Optional[str] = "America/New_York"

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    # All fields optional for partial updates

class OrganizationResponse(OrganizationBase):
    id: UUID
    slug: str
    plan: str
    compliance_tier: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

Rules:

- `Base` = shared fields
- `Create` = what the client sends to create
- `Update` = all Optional (partial updates)
- `Response` = what the API returns (includes id, timestamps)
- Always use `from_attributes = True` for ORM compatibility

## Router/Endpoint Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.models.user import User

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new organization."""
    # 1. Permission check
    if current_user.role not in ["admin", "sales"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    # 2. Business logic
    org = Organization(**data.model_dump())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    # 3. Audit log
    # 4. Return
    return org
```

Rules:

- Every endpoint has `Depends(get_current_user)` OR `Depends(get_api_key)` — no unprotected endpoints except `/auth/login`, `/auth/password/reset`, webhooks, and public review pages
- Webhooks use signature verification instead of session/key auth
- Permission checks FIRST, before any DB operations
- All DB operations use async (`await db.commit()`)
- Return Pydantic response models, never raw dicts
- HTTP status codes: 200 (success), 201 (created), 204 (deleted), 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 422 (validation error)

## Standard API Response Format

Success:

```json
{
  "id": "uuid",
  "name": "Business Name",
  "created_at": "2026-03-24T00:00:00Z"
}
```

List:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

Error:

```json
{
  "detail": "Organization not found"
}
```

Rules:

- Never wrap successful responses in `{"data": ...}` — return the object directly
- Lists always include pagination metadata
- Errors always use `detail` key (FastAPI default)

## Authentication

### Session Auth (dashboards)

```python
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    session_token = request.cookies.get("session_id")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = await redis.get(f"session:{session_token}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired")
    user = await db.get(User, uuid.UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user
```

### API Key Auth (services)

```python
async def get_api_key(request: Request, db: AsyncSession = Depends(get_db)) -> ApiKey:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    key = auth_header.replace("Bearer ", "")
    # Find by prefix, then verify hash
    prefix = key[:8]
    api_key = await db.execute(select(ApiKey).where(ApiKey.key_prefix == prefix, ApiKey.is_active == True))
    api_key = api_key.scalar_one_or_none()
    if not api_key or not bcrypt.checkpw(key.encode(), api_key.key_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid API key")
    api_key.last_used_at = datetime.utcnow()
    await db.commit()
    return api_key
```

### Dual Auth Dependency

```python
async def get_auth(request: Request, db: AsyncSession = Depends(get_db)):
    """Try session first, then API key. Returns (user, api_key) tuple."""
    session_token = request.cookies.get("session_id")
    if session_token:
        return (await get_current_user(request, db), None)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return (None, await get_api_key(request, db))
    raise HTTPException(status_code=401, detail="Not authenticated")
```

## Role Permissions

|Role       |Can Access                                                                   |
|-----------|-----------------------------------------------------------------------------|
|admin      |Everything. All orgs, all endpoints, all data.                               |
|sales      |Own org's clients, agents, bots. Cannot access admin endpoints or other orgs.|
|cold_caller|LMS only. No dashboard or API access beyond basic auth.                      |
|client     |Own org's data only. Read-only for most resources. Can update own profile.   |

Implementation: check `current_user.role` at the start of every endpoint. Use a helper:

```python
def require_role(user: User, allowed: list[str]):
    if user.role not in allowed:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
```

## Tenant Isolation

EVERY query that returns org-specific data MUST filter by `org_id`:

```python
# CORRECT
customers = await db.execute(
    select(Customer).where(Customer.org_id == current_user.org_id)
)

# WRONG — returns ALL customers across ALL orgs
customers = await db.execute(select(Customer))
```

Admin role bypasses tenant isolation for admin endpoints only.

## Audit Logging

```python
async def log_audit(db, org_id, user_id, api_key_id, action, resource_type, resource_id, details, ip):
    entry = AuditLog(
        org_id=org_id, user_id=user_id, api_key_id=api_key_id,
        action=action, resource_type=resource_type, resource_id=resource_id,
        details=details, ip_address=ip
    )
    db.add(entry)
    await db.commit()
```

Rules:

- Log EVERY create, update, delete operation
- For HIPAA orgs (`compliance_tier == 'hipaa'`): also log reads, include full request/response in `details`
- Include `api_key_id` when action performed via API key

## Error Handling

```python
# Service-level errors — raise HTTPException
raise HTTPException(status_code=404, detail="Organization not found")
raise HTTPException(status_code=400, detail="Phone number already provisioned")
raise HTTPException(status_code=409, detail="Bot already active for this organization")

# External service errors — catch and wrap
try:
    result = await stripe.Customer.create(email=org.email)
except stripe.error.StripeError as e:
    raise HTTPException(status_code=502, detail=f"Stripe error: {str(e)}")
```

Rules:

- Never return raw exception traces to the client
- External service failures return 502 (Bad Gateway)
- Always log the full error server-side before raising HTTPException

## Database Sessions

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# app/dependencies.py
async def get_db():
    async with async_session() as session:
        yield session
```

Rules:

- ALL database operations are async
- Use `async_sessionmaker`, not `sessionmaker`
- `expire_on_commit=False` to avoid lazy-load issues
- Database URL must use `postgresql+asyncpg://` prefix

## Environment Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    TELNYX_API_KEY: str
    TELNYX_MESSAGING_PROFILE_ID: str
    TELNYX_WEBHOOK_SECRET: str
    XAI_API_KEY: str = ""          # Not needed until voice bot phase
    LIVEKIT_URL: str = ""          # Not needed until voice bot phase
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    GOOGLE_API_KEY: str = ""       # Not needed until reviews bot
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
```

Rules:

- NEVER hardcode credentials
- NEVER store credentials in database
- ALL secrets loaded from environment variables via Pydantic Settings
- Optional vars have defaults (empty string) for phased rollout

## Webhook Signature Verification

```python
# Stripe
import stripe
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=401, detail="Invalid signature")
    # Process event...

# Telnyx — verify using telnyx SDK
# LiveKit — verify using livekit API key
```

Rules:

- ALL webhook endpoints verify signatures BEFORE processing
- Unverified payloads return 401 immediately
- Never trust webhook data without verification

## Testing

```python
# tests/conftest.py
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base

@pytest_asyncio.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

Rules:

- Test file per router: `test_organizations.py`, `test_auth.py`, etc.
- Every endpoint has at least: success case, auth failure case, validation error case
- Use test database (separate from dev/prod)
- Fixtures for authenticated sessions and API keys

## SMS Sending

ALWAYS check opt-out before sending:

```python
async def send_sms(db, org_id, customer_id, body, bot_type):
    customer = await db.get(Customer, customer_id)
    if customer.sms_opted_out:
        return None  # Skip silently
    phone_number = await get_primary_sms_number(db, org_id)
    result = await telnyx_service.send(from_=phone_number.number, to=customer.phone, body=body)
    # Log to message_logs
    log = MessageLog(org_id=org_id, customer_id=customer_id, bot_type=bot_type, ...)
    db.add(log)
    await db.commit()
    return result
```

-----

## Critical Execution Rules

### Dependency Pinning

- **Python:** ALL dependencies pinned to exact versions in `requirements.txt` (e.g., `fastapi==0.115.0`, NOT `fastapi>=0.115`). Run `pip freeze > requirements.txt` after adding any package. Never modify pinned versions unless explicitly upgrading.
- **Alembic migrations:** Never modify an existing migration file. Always create new migrations. Migration files are append-only.
- **Node (dashboard):** Always respect `package-lock.json` for exact dependency versions. Never delete or regenerate it. Use `npm ci` (not `npm install`) for reproducible installs.

### Chunked Execution

- **Never build an entire workstream in one go.** Break every workstream into small, testable chunks.
- **Pattern:** Write one model → verify it → write its schema → verify → write its router → verify → write tests → verify. Then move to the next model.
- **Each chunk must compile and pass tests before starting the next chunk.**
- **If a chunk fails, fix it before proceeding. Never skip ahead.**

### No Breaking Changes

- Before modifying any shared file (models/**init**.py, main.py, dependencies.py), verify that existing functionality still works.
- Run the full test suite after every change to a shared file.
- If adding a new column to an existing table, create a new Alembic migration — never modify the initial migration.

### File Ownership

- Each sub-agent owns specific files (defined in the Orchestration Plan).
- Never modify files owned by another sub-agent. Route shared file updates through the Integration Agent.
- Shared files (main.py, dependencies.py, models/**init**.py) are updated by the Integration Agent during the integration step, not by individual sub-agents.
