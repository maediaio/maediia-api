# MAEDIIA Platform Architecture

> Full platform architecture reference. Read on demand with @docs/PLATFORM_ARCHITECTURE.md
> Source of truth for schema, endpoints, and services.

---

## 1. System Overview

Hub-and-spoke architecture. FastAPI backend at api.maediia.com is the central spine.
All frontends, bots, and integrations talk to the API. No direct DB access from frontends.

### Domain Structure

| Subdomain | Purpose |
|-----------|---------|
| maediia.com | Marketing site (separate Next.js app, separate server) |
| dashboard.maediia.com | Client automation platform (Next.js 16) |
| api.maediia.com | FastAPI backend — central API for all apps |
| lms.maediia.com | Employee LMS for training |

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    dashboard.maediia.com                    │
│                    (Next.js 16 frontend)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (auth + API calls)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    api.maediia.com                          │
│                    (FastAPI backend)                        │
│  ┌─ Auth ──────────┐                                        │
│  ├─ Org CRUD ──────┤                                        │
│  ├─ Agent CRUD ────┤  ◄── Voice-specific                    │
│  ├─ Phone Mgmt ────┤  ◄── Voice-specific                    │
│  ├─ KB Upload ─────┤  ◄── Voice-specific                    │
│  ├─ Call Logs ─────┤  ◄── Voice-specific                    │
│  ├─ Webhooks ──────┤  ◄── Voice-specific                    │
│  └─ [Future bots]  ┘                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
   ┌──────────────┐ ┌──────────┐ ┌──────────────┐
   │ LiveKit Cloud│ │  Telnyx  │ │  xAI APIs    │
   │ (agents +   │ │(SIP+SMS) │ │(voice+colls) │
   │  rooms)     │ │          │ │              │
   └──────────────┘ └──────────┘ └──────────────┘
              │
   ┌──────────▼──────────────┐
   │  PostgreSQL (shared DB) │
   │  Redis (sessions + ARQ) │
   └─────────────────────────┘
```

---

## 2. Tech Stack

### Platform Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| Dashboard | Next.js 16 + TypeScript | dashboard.maediia.com |
| Backend API | FastAPI (Python, async) | api.maediia.com |
| Database | PostgreSQL (self-hosted) | Single shared DB for all apps |
| Cache / Queue | Redis + ARQ (self-hosted) | Sessions, caching, scheduled tasks |
| Auth | @maediia/shared-auth | Session cookies + API keys |
| Process Mgmt | PM2 + Supervisor | All apps managed |
| Reverse Proxy | Nginx + SSL | Let's Encrypt certificates |
| Security | Fail2ban + firewall | Server-level protection |

### Voice Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| Voice + LLM | xAI Grok Voice Agent API | Real-time speech-to-speech. $0.05/min |
| Knowledge Base | xAI Collections | Per-client KB. $2.50/1K searches |
| Orchestration | LiveKit Cloud (managed) | WebRTC/SIP rooms, agent dispatch |
| Telephony + SMS | Telnyx (primary) | Private IP backbone. ~$0.007/min |
| Telephony (secondary) | LiveKit Phone Numbers | Zero-hop US inbound for demos |
| Agent Workers | Python (livekit-agents + livekit-plugins-xai) | Hosted on LiveKit Cloud |

---

## 3. Database Schema

Single shared PostgreSQL database. All apps connect as clients.

### organizations (shared — all bots use this)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| name | VARCHAR | |
| plan | VARCHAR | Determines feature access |
| compliance_tier | VARCHAR | 'standard' or 'hipaa' |
| sms_enabled | BOOLEAN | Feature gate for post-call SMS |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### users (shared)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| org_id | UUID (FK) | |
| email | VARCHAR | |
| password_hash | VARCHAR | bcrypt |
| role | VARCHAR | Admin, Sales, Cold Caller, Client |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### agents (voice)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| org_id | UUID (FK) | |
| name | VARCHAR | e.g. 'Front Desk', 'After Hours' |
| instructions | TEXT | System prompt |
| voice | VARCHAR | xAI voice ID: Ara, Rex, Sal, Eve, Leo |
| collection_id | VARCHAR | xAI Collection ID |
| tools | JSONB | Tool configs |
| post_call_rules | JSONB | SMS/reminder automation rules |
| greeting | TEXT | |
| is_active | BOOLEAN | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### phone_numbers (voice)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| agent_id | UUID (FK) | |
| number | VARCHAR | E.164 format |
| provider | VARCHAR | 'telnyx' or 'livekit' |
| telnyx_connection_id | VARCHAR | |
| livekit_dispatch_rule_id | VARCHAR | |
| sms_enabled | BOOLEAN | |
| created_at | TIMESTAMP | |

### call_logs (voice)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| org_id | UUID (FK) | |
| agent_id | UUID (FK) | |
| direction | VARCHAR | 'inbound' or 'outbound' |
| caller_number | VARCHAR | |
| duration_seconds | INTEGER | |
| transcript | TEXT | |
| outcome | VARCHAR | booked, callback, info_sent, etc. |
| metadata | JSONB | |
| cost_cents | INTEGER | |
| created_at | TIMESTAMP | |

### sms_logs (voice — future)

Tracks all SMS messages sent via post-call automation.

### scheduled_tasks (shared — used by voice + future bots)

ARQ task queue persistence. Tracks scheduled reminders, follow-ups, etc.

### leads (shared)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| org_id | UUID (FK) | |
| name | VARCHAR | |
| phone | VARCHAR | |
| email | VARCHAR | |
| source | VARCHAR | |
| status | VARCHAR | |
| sms_opt_out | BOOLEAN | REQUIRED for compliance |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### services (shared)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| org_id | UUID (FK) | |
| name | VARCHAR | |
| duration_minutes | INTEGER | |
| price_cents | INTEGER | |
| is_active | BOOLEAN | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### appointments (shared)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID (PK) | |
| org_id | UUID (FK) | |
| lead_id | UUID (FK) | |
| service_id | UUID (FK) | |
| scheduled_at | TIMESTAMP | |
| status | VARCHAR | scheduled, confirmed, cancelled, completed |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

---

## 4. API Endpoints

### Auth (shared)
- POST /auth/login
- POST /auth/logout
- GET /auth/session
- POST /auth/api-keys — create service-to-service key
- GET /auth/api-keys — list keys for org

### Organizations (shared)
- GET /organizations/{id}
- PUT /organizations/{id}

### Agents (voice)
- POST /agents
- GET /agents/{id}
- PUT /agents/{id}
- DELETE /agents/{id}
- GET /organizations/{id}/agents

### Phone Numbers (voice)
- POST /phone-numbers/search
- POST /phone-numbers/provision
- DELETE /phone-numbers/{id}
- GET /agents/{id}/phone-numbers

### Knowledge Base (voice)
- POST /agents/{id}/knowledge-base
- GET /agents/{id}/knowledge-base
- DELETE /agents/{id}/knowledge-base/{doc_id}

### Call Logs (voice)
- GET /agents/{id}/calls
- GET /calls/{id}
- GET /organizations/{id}/calls

### Webhooks (internal)
- POST /webhooks/livekit — signature verified
- POST /webhooks/telnyx — signature verified
- POST /webhooks/stripe — signature verified
- POST /webhooks/call-outcome

---

## 5. Auth Architecture

### Dual Authentication
- **Session cookies** — dashboard users (Next.js → FastAPI)
- **API keys** — service-to-service (LiveKit agent workers → FastAPI)

### Session Details
- Redis-backed, HTTP-only cookies, 7-day duration
- bcrypt password hashing
- Roles: Admin, Sales, Cold Caller, Client

### API Key Details
- Stored hashed in DB, prefixed with 'mk_'
- Scoped per organization
- Used by LiveKit agent workers on every call to load agent config

### Webhook Auth
- ALL webhook endpoints verify provider signatures
- Stripe: stripe-signature header
- Telnyx: telnyx-signature header
- LiveKit: livekit-signature header

---

## 6. Shared Services

### Redis
- Session storage (shared with dashboard, LMS)
- ARQ task queue (post-call SMS, scheduled reminders)
- Rate limiting (per-org concurrent call limits)
- Caching (agent config cache for fast lookup during calls)

### ARQ Task Queue
- Post-call SMS via Telnyx Messaging API
- Scheduled appointment reminders
- Future bots (Birthday Bot, Recall Bot, etc.)
- Treat as shared platform service, not voice-specific

### External Services
- xAI: XAI_API_KEY env var. Voice agents connect via WebSocket. Collections API called from FastAPI.
- LiveKit Cloud: LIVEKIT_API_KEY + LIVEKIT_API_SECRET env vars.
- Telnyx: TELNYX_API_KEY env var. Number provisioning, SMS sending.
- Stripe: STRIPE_SECRET_KEY + STRIPE_WEBHOOK_SECRET env vars.

NO external service credentials stored in database. All API keys are env vars only.

---

## 7. HIPAA Compliance

When compliance_tier = 'hipaa':
- Enhanced audit logging — every API call, data access, config change logged
- Call recording encryption — transcripts encrypted at rest with per-org keys
- Stricter access controls — no bulk exports, confirmation for destructive actions
- BAA required with each HIPAA client and service providers

Hetzner does not offer HIPAA BAAs. When first HIPAA client arrives, evaluate moving to AWS/GCP.

---

## 8. Bot Plugin Pattern

Every future bot follows this pattern:
1. Define its database tables (in shared Postgres)
2. Define its API endpoints (on api.maediia.com)
3. Use shared services (auth, Redis, ARQ) — don't build its own
4. Use the platform's audit logging
5. Respect the compliance_tier flag
6. Store no credentials in the database — env vars only
