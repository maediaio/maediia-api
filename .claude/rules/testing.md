# Testing Rules

## Structure
- Test file per router: test_organizations.py, test_auth.py, etc.
- Fixtures in tests/conftest.py
- Use test database (separate from dev/prod)
- AsyncClient with ASGITransport for async tests

## Minimum Coverage Per Endpoint
- Success case
- Auth failure (no session, no API key)
- Permission failure (wrong role)
- Validation error (bad input)
- Not found (invalid ID)

## Running Tests
pytest tests/ -v
