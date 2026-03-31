# CLAUDE.md — Maediia Platform Project Memory

> **Loaded every session.** This file contains the essential context needed to work effectively on this project.

## Project Identity

**Name:** Maediia Platform (New Generation)  
**Location:** `/projects/maediia_platform/`  
**Type:** Greenfield API-first platform  
**Status:** 🚧 Foundation Phase

This is a **completely new platform**, segregated from all existing Maediia code. Fresh architecture, fresh patterns, fresh everything.

## Core Architecture

- **Backend:** Python/FastAPI
- **Database:** PostgreSQL + Alembic migrations
- **ORM:** SQLAlchemy 2.0
- **Auth:** JWT-based with refresh tokens
- **Testing:** pytest with async support
- **Deployment:** Docker + Docker Compose

## Project Structure

```
maediia-api/
├── app/                    # Main application code
│   ├── api/               # API routes
│   ├── core/              # Config, security, logging
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── db/                # Database utilities
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
└── docs/                  # Reference documentation
```

## Current Phase

See `PROGRESS.md` for detailed build status.

## Key Conventions

1. **Read `.claude/rules/`** before implementing features
2. **Update `PROGRESS.md`** after every significant change
3. **Use `/verify-phase`** to check current phase completion
4. **Reference `@docs/`** for architectural decisions

## Active Decisions

- [Document key architectural decisions here as they're made]

## Blockers & Questions

- [Track anything blocking progress]

---

*Last updated: 2026-03-31*  
*Session: Foundation setup*
