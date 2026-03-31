# Database Rules & Patterns

> Auto-loaded by Claude. Defines database conventions for the Maediia Platform.

## Technology Stack

- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Driver:** `asyncpg`

## Model Patterns

### Base Model
```python
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Base model with common columns."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
```

### Entity Model Template
```python
class User(Base):
    """User entity."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    calls: Mapped[list["Call"]] = relationship(back_populates="user")
```

## Naming Conventions

- **Tables:** Plural, `snake_case` (e.g., `users`, `voice_sessions`)
- **Columns:** `snake_case`
- **Indexes:** `ix_tablename_columnname`
- **Constraints:** 
  - PK: `pk_tablename`
  - FK: `fk_tablename_referencedtable_columnname`
  - Unique: `uq_tablename_columnname`

## Migration Rules

1. **Always use Alembic** — never modify DB directly
2. **One change per migration** — atomic commits
3. **Test migrations** against fresh DB before commit
4. **Never delete** migrations after they've been applied

### Creating Migrations
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "add user table"

# Manual migration
alembic revision -m "custom data migration"
```

## Query Patterns

### Async Session
```python
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### Transactions
```python
async def transfer_credits(db: AsyncSession, from_id: int, to_id: int, amount: int) -> None:
    async with db.begin():
        from_user = await get_user(db, from_id)
        to_user = await get_user(db, to_id)
        
        from_user.credits -= amount
        to_user.credits += amount
        
        # Commit happens automatically at end of context
```

## Performance Guidelines

- **Always index** foreign keys
- **Index** columns used in WHERE, ORDER BY, JOIN
- **Use `selectinload`** for relationships to avoid N+1
- **Paginate** all list queries (default: 20, max: 100)

---

*Validated by: alembic, SQLAlchemy 2.0 best practices*
