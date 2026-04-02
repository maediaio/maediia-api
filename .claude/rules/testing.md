# Testing Rules

> Reference these rules before writing any tests.

---

## Structure

- Test file per router: test_auth.py, test_agents.py, test_organizations.py, etc.
- All fixtures in tests/conftest.py
- Separate test database — never run tests against dev or prod DB
- Use AsyncClient with ASGITransport for async tests

---

## Required Test Coverage Per Endpoint

Every endpoint must have tests for:
1. Success case — happy path, correct data returned
2. Auth failure — no session cookie, no API key
3. Permission failure — wrong role
4. Validation error — bad input data
5. Not found — invalid ID or wrong org

---

## Test File Structure

tests/
- conftest.py — shared fixtures
- test_auth.py
- test_organizations.py
- test_agents.py
- test_phone_numbers.py
- test_knowledge_base.py
- test_call_logs.py
- test_webhooks.py

---

## conftest.py Fixtures

from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost/maediia_test"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def admin_user(db_session):
    user = User(
        org_id=test_org.id,
        email="admin@test.com",
        password_hash=hash_password("testpass"),
        role="admin"
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest_asyncio.fixture
async def auth_headers(client, admin_user):
    response = await client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "testpass"
    })
    token = response.cookies.get("session")
    return {"Cookie": f"session={token}"}

---

## Example Test

import pytest
from httpx import AsyncClient

class TestAgents:

    async def test_get_agent_success(self, client, auth_headers, test_agent):
        response = await client.get(f"/agents/{test_agent.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == str(test_agent.id)

    async def test_get_agent_no_auth(self, client, test_agent):
        response = await client.get(f"/agents/{test_agent.id}")
        assert response.status_code == 401

    async def test_get_agent_wrong_role(self, client, cold_caller_headers, test_agent):
        response = await client.get(f"/agents/{test_agent.id}", headers=cold_caller_headers)
        assert response.status_code == 403

    async def test_get_agent_not_found(self, client, auth_headers):
        response = await client.get("/agents/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404

    async def test_get_agent_wrong_org(self, client, other_org_headers, test_agent):
        response = await client.get(f"/agents/{test_agent.id}", headers=other_org_headers)
        assert response.status_code == 404

---

## Running Tests

Run all tests:
pytest tests/ -v

Run with coverage:
pytest tests/ -v --cov=app --cov-report=html

Run single file:
pytest tests/test_agents.py -v

Run single test:
pytest tests/test_agents.py::TestAgents::test_get_agent_success -v

---

## Test Database

Never run tests against dev or production database.
Set TEST_DATABASE_URL in .env.test
Create test DB before first run:
createdb maediia_test

Tests use transactions that rollback after each test — DB stays clean.

---

## Webhook Testing

For webhook endpoints, test signature verification:

async def test_webhook_invalid_signature(self, client):
    response = await client.post(
        "/webhooks/telnyx",
        json={"event": "call.initiated"},
        headers={"telnyx-signature-ed25519": "invalid"}
    )
    assert response.status_code == 400

async def test_webhook_valid_signature(self, client, mock_telnyx_signature):
    response = await client.post(
        "/webhooks/telnyx",
        json={"event": "call.initiated"},
        headers={"telnyx-signature-ed25519": mock_telnyx_signature}
    )
    assert response.status_code == 200
