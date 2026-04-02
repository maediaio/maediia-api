# MAEDIIA Platform API

## What This Is
Business automation platform API (api.maediia.com). Hub-and-spoke architecture — this FastAPI backend is the central API that all frontends, bots, and integrations talk to. PostgreSQL + Redis on VPS. Voice agents run on LiveKit Cloud.

## Tech Stack
- Backend: FastAPI (Python, async)
- Database: PostgreSQL (self-hosted, SQLAlchemy + Alembic)
- Cache/Queue: Redis + ARQ
- Auth: Session cookies (dashboard users) + API keys (service-to-service)
- Billing: Stripe (per-bot subscriptions)
- Messaging: Telnyx (SMS for all bots)
- Voice: xAI Grok Voice Agent API + LiveKit Cloud + Telnyx SIP

## Architecture Rules
- One database, all apps. No JSON files, no SQLite.
- One API, all consumers. No direct DB access from frontends.
- Bots are plugins. Each adds its own tables + endpoints, uses shared services.
- Per-bot billing via Stripe subscription items.
- HIPAA-ready by default. Encryption everywhere, audit logging, compliance_tier flag.
- Dual auth: session cookies for dashboards, API keys for agent workers/services.
- All webhook endpoints verify signatures before processing.

## Code Conventions
See @.claude/rules/conventions.md for full standards. Key rules:
- SQLAlchemy models: PascalCase singular, UUID PKs, created_at + updated_at on all mutable tables
- Pydantic schemas: Base/Create/Update/Response pattern
- Routers: every endpoint has auth dependency, permission check first, audit log after
- Tenant isolation: EVERY org-scoped query filters by org_id
- Errors: HTTPException with correct status codes, never raw traces
- DB: ALL operations async (asyncpg)
- Secrets: NEVER hardcoded, always from env vars via app/config.py
- Dependency pinning: requirements.txt with exact versions (==)
- Alembic: migrations are append-only, never modify existing ones

## Current Build Phase
Check @PROGRESS.md for current status and next steps.

## Reference Docs
- @docs/PLATFORM_ARCHITECTURE.md — full schema, all endpoints, all services
- @docs/VOICE_CONTRACT.md — voice bot requirements from the platform
- @docs/BUILD_CHECKLISTS.md — verification checklists per phase
- @.claude/rules/ — detailed code standards by topic

## Build Phases (Sequential)
Phase 0: Platform spine (DB + FastAPI + auth + Stripe + Telnyx + Redis)
Part 1: Voice agent POC (LiveKit + xAI + Telnyx)
Part 2: Knowledge base (xAI Collections)
Part 3: Multi-tenant routing
Part 4: Voice API endpoints + post-call automation
Part 5: Dashboard frontend
Part 6: Website voice widget
Part 7: Production hardening

## Phase 0 Execution Order
1. Database schema (all models + Alembic migration)
2. FastAPI core (app scaffold, auth middleware, all CRUD routers)
3. Redis + ARQ (sessions, task queue, worker)
4. Stripe integration (billing service, webhook handler)
5. Telnyx integration (messaging service, webhook handler)
6. Data migration (users.json → Postgres)
7. Nginx + deployment (api.maediia.com live)

## Session Workflow
1. Read PROGRESS.md to see where we left off
2. Continue building the current phase step by step
3. Test each piece before moving to the next
4. Before ending session: run /progress-update to save state
