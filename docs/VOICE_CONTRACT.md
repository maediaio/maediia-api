# Voice Reception Bot — Platform Architecture Contract

> This document defines what the AI Reception Bot requires from the MAEDIIA platform.
> It is the contract between the platform (api.maediia.com) and the voice reception feature.
> Last Updated: March 2026 | Status: Architecture finalized. Build not yet started.

---

## 1. Stack Decisions (Confirmed — Non-Negotiable)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Voice AI | xAI Grok Voice Agent API | Speech-to-speech. $0.05/min. us-east-1 only. |
| Orchestration | LiveKit Cloud (managed) | Agent hosting, SIP/WebRTC rooms, dispatch. |
| Telephony + SMS | Telnyx (primary) | Private IP backbone. ~$0.007/min. |
| Telephony (secondary) | LiveKit Phone Numbers | US inbound only. Zero-hop for demos. |
| Knowledge Base | xAI Collections | Per-client KB. $2.50/1K searches. No external vector DB. |
| Agent Workers | Python (livekit-agents + livekit-plugins-xai) | Hosted on LiveKit Cloud. |
| Task Queue | Redis + ARQ | Post-call SMS, scheduled reminders. Shared with platform. |

---

## 2. Database Tables Required

### organizations (shared)
- id, name, plan, compliance_tier, sms_enabled
- compliance_tier triggers enhanced audit logging for HIPAA clients

### users (shared)
- id, org_id, email, password_hash, role
- role controls dashboard access to voice settings

### agents (voice)
- id, org_id, name, instructions, voice, collection_id
- tools (JSONB), post_call_rules (JSONB), greeting, is_active
- created_at, updated_at

### phone_numbers (voice)
- id, agent_id, number (E.164), provider
- telnyx_connection_id, livekit_dispatch_rule_id, sms_enabled

### call_logs (voice)
- id, org_id (FK — REQUIRED), agent_id (FK)
- direction, caller_number, duration_seconds
- transcript, outcome, metadata (JSONB), cost_cents
- created_at, updated_at

### sms_logs (voice — future)
- Tracks all SMS sent via post-call automation
- Must include sms_opt_out check before sending

### scheduled_tasks (shared)
- ARQ task queue persistence
- Used by voice + all future bots

---

## 3. API Endpoints Required

### Auth (shared)
- POST /auth/login
- POST /auth/logout
- GET /auth/session
- POST /auth/api-keys — for agent worker service accounts

### Organizations (shared)
- GET /organizations/{id}
- PUT /organizations/{id}

### Agents (voice)
- POST /agents
- GET /agents/{id} — called by agent workers on EVERY call
- PUT /agents/{id}
- DELETE /agents/{id}
- GET /organizations/{id}/agents

### Phone Numbers (voice)
- POST /phone-numbers/search
- POST /phone-numbers/provision — one-click: buy number + LiveKit trunk + dispatch rule + DB
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

### Webhooks (internal — all signature verified)
- POST /webhooks/livekit
- POST /webhooks/telnyx
- POST /webhooks/call-outcome — triggers post-call automation

---

## 4. Post-Call Automation

Not exposed as API endpoints — runs as background logic via ARQ.

On call end:
1. Evaluate outcome against agent's post_call_rules
2. Immediate: send SMS via Telnyx Messaging API (if sms_opt_out = false)
3. Delayed: enqueue task in ARQ with future execution time

---

## 5. Shared Services Used

### @maediia/shared-auth
- Same auth as all MAEDIIA apps
- Redis-backed sessions, HTTP-only cookies, 7-day duration
- FastAPI validates sessions against same Redis store
- API keys for agent workers (service-to-service)

### Redis
- Session storage
- ARQ task queue
- Rate limiting (per-org concurrent call limits)
- Agent config cache (fast lookup during calls — critical for latency)

---

## 6. External Service Integration

| Service | Integration Details |
|---------|-------------------|
| xAI API | XAI_API_KEY env var. Voice agents connect via WebSocket. Collections API called from FastAPI. |
| LiveKit Cloud | LIVEKIT_API_KEY + LIVEKIT_API_SECRET env vars. Agent workers hosted on LiveKit Cloud. |
| Telnyx | TELNYX_API_KEY env var. FastAPI calls Telnyx for number provisioning + SMS sending. |

No credentials in database. All API keys are environment variables only.

---

## 7. HIPAA Behavior

When compliance_tier = 'hipaa':
- Enhanced audit logging on every API call, data access, config change
- Transcripts encrypted at rest with per-org keys
- No bulk data exports
- BAA tracking per org (signed/pending/not required)

---

## 8. What This Means for Other Bots

Every future bot follows the same pattern:
1. Define its DB tables in shared Postgres
2. Define its endpoints on api.maediia.com
3. Use shared services — don't build its own
4. Use the platform's audit logging
5. Respect compliance_tier flag
6. No credentials in DB — env vars only
