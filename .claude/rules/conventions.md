# MAEDIIA Code Conventions

> Loaded every session. Follow these standards for all code in this project.

---

## File & Module Structure

- One model per file in app/models/
- One router per file in app/api/routers/
- One service per file in app/services/
- All models imported in app/models/__init__.py
- All routers registered in app/api/__init__.py

## Naming Conventions

- Models: PascalCase singular (Organization, User, Agent, CallLog)
- Routers/files: snake_case (call_logs.py, phone_numbers.py)
- Functions: snake_case (get_agent_by_id, create_call_log)
- Constants: UPPER_SNAKE_CASE (MAX_CONCURRENT_CALLS)
- Pydantic schemas: PascalCase with suffix (AgentCreate, AgentUpdate, AgentResponse)

## SQLAlchemy Models

Every model MUST have:
- UUID primary key: id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
- created_at: created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
- updated_at on ALL mutable tables: updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
- Nullable FKs explicitly marked: nullable=True
- JSONB columns: from sqlalchemy.dialects.postgresql import JSONB
- Relationships use back_populates on both sides

Example model:
```python
class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    instructions = Column(Text, nullable=True)
    voice = Column(String, nullable=False, default="Ara")
    collection_id = Column(String, nullable=True)
    tools = Column(JSONB, nullable=True)
    post_call_rules = Column(JSONB, nullable=True)
    greeting = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="agents")
    phone_numbers = relationship("PhoneNumber", back_populates="agent")
```

## Pydantic Schemas

Use Base/Create/Update/Response pattern:
```python
class AgentBase(BaseModel):
    name: str
    voice: str = "Ara"
    greeting: Optional[str] = None

class AgentCreate(AgentBase):
    org_id: UUID
    instructions: str

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    instructions: Optional[str] = None
    voice: Optional[str] = None
    is_active: Optional[bool] = None

class AgentResponse(AgentBase):
    id: UUID
    org_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

## API Routers

Every endpoint MUST:
1. Have auth dependency: Depends(get_current_user) OR Depends(get_api_key)
2. Do permission check FIRST before any DB operation
3. Filter by org_id for ALL org-scoped queries (tenant isolation)
4. Write audit log AFTER successful operation
5. Use HTTPException with correct status codes
6. Never return raw exception traces
```python
@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Permission check first
    if current_user.role not in ["admin", "sales", "client"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # 2. Tenant isolation — always filter by org_id
    agent = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.org_id == current_user.org_id  # NEVER skip this
        )
    )
    agent = agent.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent
```

## Database Operations

- ALL operations must be async (asyncpg driver)
- Database URL prefix: postgresql+asyncpg://
- Use AsyncSession from sqlalchemy.ext.asyncio
- Always use select() not query()
- Use scalar_one_or_none() for single results
- Use scalars().all() for lists

## Error Handling

Status codes:
- 200: success
- 201: created
- 204: deleted (no content)
- 400: bad request (invalid input)
- 401: unauthorized (no/invalid auth)
- 403: forbidden (insufficient permissions)
- 404: not found
- 422: validation error (Pydantic handles automatically)
- 502: external service error (xAI, Telnyx, LiveKit down)

## Secrets & Configuration

- NEVER hardcode secrets
- All secrets from environment variables via app/config.py
- Use pydantic BaseSettings for config
- .env file for local dev (never committed)
- .env.example with all required keys (no values)

## Dependencies & Requirements

- requirements.txt with exact versions (==)
- Never use >= or ~= in requirements.txt
- Pin ALL dependencies including transitive ones

## Alembic Migrations

- Migrations are APPEND-ONLY
- NEVER modify existing migration files
- Always create new migration for schema changes
- Migration naming: descriptive snake_case
- Test migrations up AND down before committing

## Testing

- Test file per router: test_agents.py, test_auth.py, etc.
- Use AsyncClient with ASGITransport
- Separate test database
- Fixtures in tests/conftest.py
- Minimum per endpoint: success, auth failure, permission failure, not found

## Audit Logging

Every write operation (POST, PUT, DELETE) must log:
- user_id
- action (created, updated, deleted)
- resource_type (agent, phone_number, etc.)
- resource_id
- timestamp
- ip_address

HIPAA-tier orgs get additional logging on all GET operations.
