# Code Conventions

> Auto-loaded by Claude. Defines coding standards for the Maediia Platform.

## Python Standards

### Style
- **PEP 8** compliance (enforced by ruff)
- **Line length:** 100 characters max
- **Quotes:** Double quotes for strings
- **Imports:** `isort` with "black" profile

### Naming
- **Modules:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions/Variables:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore`

### Type Hints
- **Required** on all function signatures
- Use `from __future__ import annotations` for forward refs
- Prefer `|` over `Union` and `Optional`

```python
# Good
def get_user(user_id: int) -> User | None:
    ...

# Bad
def get_user(user_id: int) -> Optional[User]:
    ...
```

## FastAPI Patterns

### Route Organization
```
app/api/
├── deps.py          # Dependencies (auth, db, etc.)
├── v1/
│   ├── __init__.py
│   ├── auth.py      # /api/v1/auth/*
│   ├── users.py     # /api/v1/users/*
│   └── voice.py     # /api/v1/voice/*
└── router.py        # Aggregate router
```

### Endpoint Pattern
```python
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get a user by ID."""
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)
```

## Async Patterns

- **Database:** Use `asyncpg` + SQLAlchemy async session
- **External APIs:** Use `httpx.AsyncClient`
- **Background tasks:** FastAPI `BackgroundTasks` or Celery for heavy work

## Error Handling

```python
# Custom exception hierarchy
class MaediiaException(Exception):
    """Base exception."""
    pass

class NotFoundException(MaediiaException):
    """Resource not found."""
    pass

class ValidationException(MaediiaException):
    """Invalid input."""
    pass
```

## Documentation

- **Docstrings:** Google style
- **API docs:** Auto-generated from OpenAPI
- **README:** Update when adding major features

---

*Enforced by: ruff, mypy, pre-commit hooks*
