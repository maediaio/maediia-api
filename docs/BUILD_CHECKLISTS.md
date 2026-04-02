# MAEDIIA Build Checklists

> Used by /verify-phase slash command to check phase completion.
> Run through each item and report pass/fail.

---

## Phase 0: Platform Spine

### Step 1: Database Schema
- [ ] All SQLAlchemy models created (organizations, users, agents, phone_numbers, call_logs, sms_logs, scheduled_tasks, leads, services, appointments)
- [ ] All models have UUID primary keys
- [ ] All mutable tables have created_at + updated_at
- [ ] All foreign keys defined correctly
- [ ] JSONB columns used for tools, post_call_rules, metadata
- [ ] Alembic initial migration created
- [ ] Alembic migration runs without errors
- [ ] All models imported in app/models/__init__.py

### Step 2: FastAPI Core
- [ ] FastAPI app scaffold created (app/main.py)
- [ ] All routers registered (auth, organizations, agents, phone_numbers, knowledge_base, call_logs, webhooks)
- [ ] Auth middleware implemented (session cookies + API keys)
- [ ] get_current_user dependency working
- [ ] get_api_key dependency working
- [ ] Permission checks on all protected endpoints
- [ ] Tenant isolation — all org-scoped queries filter by org_id
- [ ] HTTPException used for all errors (no raw traces)
- [ ] Health check endpoint at GET /health

### Step 3: Redis + ARQ
- [ ] Redis connection configured
- [ ] Session storage working
- [ ] ARQ worker configured
- [ ] ARQ task queue working
- [ ] Test task enqueues and executes successfully

### Step 4: Stripe Integration
- [ ] Stripe client configured (STRIPE_SECRET_KEY env var)
- [ ] Webhook handler at POST /webhooks/stripe
- [ ] Stripe signature verification working
- [ ] Subscription creation working
- [ ] Subscription cancellation working

### Step 5: Telnyx Integration
- [ ] Telnyx client configured (TELNYX_API_KEY env var)
- [ ] SMS sending working via Telnyx Messaging API
- [ ] Webhook handler at POST /webhooks/telnyx
- [ ] Telnyx signature verification working
- [ ] Phone number search working
- [ ] Phone number provisioning working

### Step 6: Data Migration
- [ ] Existing users.json read and parsed
- [ ] Users migrated to PostgreSQL
- [ ] Existing org data migrated
- [ ] Migration script idempotent (safe to run multiple times)
- [ ] Verification: user count matches before/after

### Step 7: Nginx + Deployment
- [ ] api.maediia.com DNS configured
- [ ] Nginx server block configured
- [ ] SSL certificate issued (Let's Encrypt)
- [ ] FastAPI running under Supervisor
- [ ] Health check at https://api.maediia.com/health returns 200
- [ ] Auth flow working end-to-end from dashboard

---

## Voice Reception — Part 1: Single Agent POC

- [ ] LiveKit Cloud account configured
- [ ] xAI API key working
- [ ] Telnyx SIP trunk created
- [ ] Single agent connects to LiveKit room
- [ ] xAI voice responds to caller
- [ ] Call ends cleanly
- [ ] Basic transcript captured

## Voice Reception — Part 2: Knowledge Base

- [ ] xAI Collection created for test org
- [ ] Documents uploaded to Collection
- [ ] Agent queries Collection during call
- [ ] Responses grounded in KB content
- [ ] Collection ID stored in agents table

## Voice Reception — Part 3: Multi-Tenant Routing

- [ ] Multiple orgs in database
- [ ] Each org has own agent + phone number
- [ ] Inbound call routes to correct agent by phone number
- [ ] Agent loads config from FastAPI (GET /agents/{id})
- [ ] API key auth working for agent workers
- [ ] Tenant isolation confirmed — no cross-org data access

## Voice Reception — Part 4: Voice API + Post-Call

- [ ] All voice endpoints implemented and tested
- [ ] POST /webhooks/call-outcome receives and processes outcomes
- [ ] Post-call SMS sends via Telnyx (sms_opt_out checked)
- [ ] Delayed tasks enqueue in ARQ correctly
- [ ] Call logs written to DB on every call
- [ ] Cost calculation working

## Voice Reception — Part 5: Dashboard Frontend

- [ ] Agent management UI (create, edit, delete)
- [ ] Phone number provisioning UI
- [ ] Knowledge base upload UI
- [ ] Call logs table with filters
- [ ] Real-time analytics (call volume, outcomes)
- [ ] Auth integrated with @maediia/shared-auth

## Voice Reception — Part 6: Website Voice Widget

- [ ] LiveKit Web SDK integrated
- [ ] Widget embeddable on maediia.com
- [ ] Connects to demo agent
- [ ] Works on mobile browsers

## Voice Reception — Part 7: Production Hardening

- [ ] Load testing completed
- [ ] Error handling covers all edge cases
- [ ] Monitoring alerts configured
- [ ] Backup system verified
- [ ] HIPAA audit logging verified for hipaa-tier orgs
- [ ] Rate limiting tested
- [ ] All API keys rotated from dev to production values
- [ ] Documentation updated

---

## Verification Instructions

For each checklist item:
1. Check if the file/table/endpoint exists
2. Run relevant tests if applicable
3. Mark pass ✅ or fail ❌
4. List any failing items with notes on what's needed

Report format:
- Total items: X
- Passed: X
- Failed: X
- Needs attention: [list]
