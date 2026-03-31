# Database Rules

## Schema Reference
Full schema with all tables and columns: @docs/PLATFORM_ARCHITECTURE.md Section 3

## Rules
- ALL primary keys: UUID with uuid.uuid4 default
- ALL foreign keys: UUID(as_uuid=True)
- ALL tables: created_at with datetime.utcnow default
- ALL mutable tables: updated_at with onupdate=datetime.utcnow
- Nullable FKs explicitly marked nullable=True
- JSONB columns use sqlalchemy.dialects.postgresql.JSONB
- Relationships use back_populates on both sides
- One model per file in app/models/
- All models imported in app/models/__init__.py
- Alembic migrations: NEVER modify existing, always create new
- Database URL must use postgresql+asyncpg:// prefix
