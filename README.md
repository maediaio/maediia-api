# Maediia API

> The core API platform for Maediia's voice reception services.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Setup

```bash
# Clone and navigate
cd /projects/maediia_platform/maediia-api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Docker (Alternative)

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# View logs
docker-compose logs -f api
```

## Project Structure

```
maediia-api/
├── app/                    # Main application
│   ├── api/               # API routes
│   ├── core/              # Config, security, logging
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── db/                # Database utilities
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

## Development Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy app/

# Create migration
alembic revision --autogenerate -m "description"
```

## API Documentation

Once running, view interactive docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Environment Variables

See `.env.example` for all required variables.

## Claude Commands

This project supports custom slash commands:

- `@verify-phase` — Run checklist for current phase
- `@progress-update` — Update PROGRESS.md
- `@next-phase` — Show what to build next

## Architecture

See `docs/` for detailed architecture docs:

- `PLATFORM_ARCHITECTURE.md` — System overview
- `VOICE_CONTRACT.md` — Voice API contract
- `BUILD_CHECKLISTS.md` — Phase verification

## License

Private — Maediia Technologies
