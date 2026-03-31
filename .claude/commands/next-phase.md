# /next-phase

## Purpose
Show what to build next based on current phase.

## Usage
```
@next-phase
```

## Phase Overview

| Phase | Name | Status |
|-------|------|--------|
| 0 | Foundation | 🚧 In Progress |
| 1 | Core API Skeleton | ⏳ Not Started |
| 2 | Authentication System | ⏳ Not Started |
| 3 | Voice Reception Contract | ⏳ Not Started |

## Current Phase: Foundation (0)

### Ready to Start
1. Create `README.md`
2. Create `.env.example`
3. Create `requirements.txt`
4. Populate `docs/` with architecture docs

### Prerequisites for Phase 1
- [ ] All Phase 0 items complete
- [ ] Docker Compose configured
- [ ] Basic FastAPI dependencies listed

## Phase 1 Preview: Core API Skeleton

When you're ready:

1. **App Factory** — `app/main.py` with create_app()
2. **Health Endpoint** — `GET /health` returning status
3. **Database Setup** — SQLAlchemy async engine + session
4. **Config Management** — Pydantic Settings with .env
5. **Logging** — Structured logging setup
6. **Docker** — docker-compose.yml for local dev

Run `@next-phase` anytime to see this again.
