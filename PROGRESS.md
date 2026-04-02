# MAEDIIA Build Progress

> Updated at end of every session using /progress-update

---

## Phase 0: Platform Spine

| Step | Status | Notes |
|------|--------|-------|
| Database schema (models + migration) | ✅ Complete | 14 models, 4 migrations. ReadOnlyBase for log tables (CallLog, SmsLog, Voicemail, AuditLog) |
| FastAPI core (scaffold, auth, CRUD routers) | ✅ Complete | 9 routers, 30 endpoints, schemas, audit service, ApiKey model. Self-audit + fixes applied. |
| Redis + ARQ setup | ✅ Complete | Redis pool + ARQ pool on lifespan. Session service (create/get/delete/refresh). ARQ worker (WorkerSettings, startup/shutdown). Task functions: send_sms, send_appointment_reminder. Queue service with ScheduledTask persistence. |
| Stripe integration | ✅ Complete | stripe.StripeClient async methods. create_customer, create_subscription, cancel_subscription, get_subscription. Webhook handler: subscription.created/updated/deleted syncs org.plan, invoice.payment_failed logged. Migration adds stripe_customer_id + stripe_subscription_id to organizations. |
| Telnyx integration | ✅ Complete | telnyx_service.py: search_numbers, purchase_number, release_number, send_sms, verify_signature (all asyncio.to_thread wrapped). SMS task wired. phone_numbers + business_lines routers wired. Telnyx webhook: Ed25519 verified, call/SMS events handled. TELNYX_SIP_CONNECTION_ID added to config. |
| Data migration (JSON → Postgres) | N/A | Fresh build — no legacy data to migrate |
| Nginx + deployment (api.maediia.com live) | ✅ Complete | deploy/nginx/api.maediia.com.conf, deploy/supervisor/maediia-api.conf + maediia-worker.conf, deploy/deploy.sh (--setup first-deploy + redeploy with health check). 40 routes confirmed. |

## Voice Reception

| Step | Status | Notes |
|------|--------|-------|
| Part 1: Single agent POC | ⬜ Not Started | |
| Part 2: Knowledge base (xAI Collections) | ⬜ Not Started | |
| Part 3: Multi-tenant routing | ⬜ Not Started | |
| Part 4: Voice API + post-call automation | ⬜ Not Started | |
| Part 5: Dashboard frontend | ⬜ Not Started | |
| Part 6: Website voice widget | ⬜ Not Started | |
| Part 7: Production hardening | ⬜ Not Started | |

## Decisions

- Auth: session cookies (dashboard users) + API keys (agent workers) — NOT JWT
- No API versioning (/api/v1 removed) — flat routing
- LiveKit Cloud managed (not self-hosted)
- Telnyx replacing Twilio
- xAI Grok Voice Agent API for voice
- Single shared PostgreSQL DB for all apps
- ReadOnlyBase (created_at only) vs Base (created_at + updated_at) — log tables use ReadOnlyBase
- Virtual Business Line feature added before Step 2 — business_lines + voicemails tables + 8 endpoints
- livekit-agents pinned to 1.5.1 (0.10.3 does not exist on PyPI)
- Two Redis pools on same connection: redis.asyncio pool (sessions/cache) + ARQ pool (task queue). Both managed in app/services/redis.py lifespan.
- ARQ worker runs as separate process: `python -m arq app.worker.WorkerSettings`
- Task functions are stubs until Telnyx wired in Step 5 — send_sms returns "stub_not_sent"
- enqueue() flushes before ARQ call to guarantee task.id exists for arq_job_id linkage
- Stripe async uses stripe.StripeClient + _async method suffix (e.g. create_async) — stripe.AsyncStripe does not exist in v11.4.1
- org.plan derived from Stripe subscription metadata["plan"] first, then price.nickname — no hardcoded price IDs in code
- Stripe webhook uses construct_event() which verifies + parses in one step — no separate verify step needed
- telnyx library v2.1.3 is fully synchronous — all calls wrapped in asyncio.to_thread() to avoid blocking event loop
- Telnyx webhook requires both telnyx-signature-ed25519 AND telnyx-timestamp headers for Ed25519 verification
- send_sms task now requires from_number param — caller (post-call automation, business line) must supply sender number
- TELNYX_SIP_CONNECTION_ID env var needed for voice number provisioning — set once in Telnyx dashboard, referenced per purchase
- deploy/deploy.sh --setup handles full first-deploy (packages, venv, nginx, certbot, supervisor, migrations). Plain run handles redeployment.
- uvicorn runs with 4 workers + uvloop + proxy-headers behind Nginx on 127.0.0.1:8000

## Issues

- ~~Redis session service stub in security.py needs implementation in Phase 0 Step 3 (all auth endpoints return 401 until then)~~ — resolved in Step 3
- ~~Telnyx integration stubs return 501~~ — resolved in Step 5. LiveKit stubs remain, implemented in Part 1.
- Knowledge base endpoints return 501 — implemented in Part 2 (xAI Collections)
- ~~Webhook signature verification stubbed~~ — Stripe and Telnyx fully wired. LiveKit stub remains (Part 1).
- git push requires credentials not available in build environment — push from local machine
- Self-audit (Phase 0 close): CRITICAL fixed — send_appointment_reminder was missing from_number param (would TypeError at runtime). WARN fixed — Stripe webhook and SMS _mark_complete had unguarded db.commit() calls. WARN fixed — /webhooks/call-outcome was doing format-only API key check, replaced with real DB hash lookup. INFO fixed — Voicemail missing organization relationship on both sides.

## Last Session

Date: 2026-04-02
Work done: Phase 0 complete. Steps 5–7 + self-audit. Step 7: Nginx config, Supervisor configs (API + worker), deploy.sh. Self-audit: 1 critical fix (reminder task missing from_number), 3 warn fixes (unguarded commits in Stripe webhook + SMS task, call-outcome API key format-only check replaced with DB lookup), 1 info fix (Voicemail/Organization relationship gap). All 40 routes confirmed clean on import.
Next: Voice Reception Part 1 — Single agent POC (LiveKit + xAI + Telnyx SIP)
