"""Test configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator

# Import app for testing
from app.main import create_app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    """Create app instance for testing."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create test client."""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
