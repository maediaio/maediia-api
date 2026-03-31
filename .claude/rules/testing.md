# Testing Rules & Patterns

> Auto-loaded by Claude. Defines testing standards for the Maediia Platform.

## Testing Stack

- **Framework:** pytest + pytest-asyncio
- **Coverage:** pytest-cov (target: 80%+)
- **Factories:** pytest-factoryboy
- **Fixtures:** Shared fixtures in `conftest.py`
- **Mocking:** pytest-mock + unittest.mock

## Directory Structure

```
tests/
├── conftest.py           # Global fixtures
├── factories.py          # Model factories
├── unit/                 # Unit tests (no DB)
│   ├── test_services.py
│   └── test_utils.py
├── integration/          # Integration tests (with DB)
│   ├── test_api/
│   │   ├── test_auth.py
│   │   └── test_users.py
│   └── test_db/
└── e2e/                  # End-to-end tests
    └── test_voice_flow.py
```

## Test Naming

```python
# Function names
def test_user_service_raises_not_found_for_invalid_id():
    ...

# Class-based
def TestUserService:
    def test_get_by_id_returns_user(self):
        ...
    
    def test_get_by_id_raises_when_not_found(self):
        ...
```

## Fixtures Pattern

```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.main import app
from app.api.deps import get_db

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db(engine) -> AsyncSession:
    """Provide test database session."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db):
    """Provide test HTTP client with overridden DB."""
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
```

## Factory Pattern

```python
# factories.py
import factory
from app.models.user import User

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    hashed_password = factory.LazyAttribute(lambda _: hash_password("password123"))
    is_active = True
```

## Test Patterns

### Unit Test
```python
# tests/unit/test_services.py
import pytest
from app.services.user import UserService
from app.exceptions import NotFoundException

@pytest.mark.asyncio
async def test_user_service_get_by_id_raises_not_found():
    # Arrange
    service = UserService()
    mock_db = Mock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    # Act & Assert
    with pytest.raises(NotFoundException):
        await service.get_by_id(mock_db, 999)
```

### Integration Test
```python
# tests/integration/test_api/test_auth.py
import pytest

@pytest.mark.asyncio
async def test_login_returns_tokens(client, db):
    # Arrange
    from tests.factories import UserFactory
    user = UserFactory()
    db.add(user)
    await db.commit()
    
    # Act
    response = await client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": "password123"
    })
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/integration/test_api/test_auth.py

# With debugging
pytest -v --tb=short -x

# Async tests only
pytest -m asyncio
```

## Coverage Targets

| Component | Target |
|-----------|--------|
| Models | 90% |
| Services | 85% |
| API endpoints | 80% |
| Utils/helpers | 75% |

---

*Validated by: pytest, coverage reports*
