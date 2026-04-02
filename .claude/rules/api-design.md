# API Design Rules

> Reference these rules before creating or modifying any API endpoints.

---

## Endpoint Reference

Full endpoint list: @docs/PLATFORM_ARCHITECTURE.md Section 4

---

## Authentication

Every endpoint MUST have one of these dependencies:
- Depends(get_current_user) — for dashboard users (session cookie)
- Depends(get_api_key) — for service-to-service (agent workers)

Exceptions (no auth required):
- POST /auth/login
- POST /auth/password/reset
- POST /webhooks/* — use signature verification instead
- GET /health

Webhooks use signature verification, not session auth:
- Stripe: verify stripe-signature header
- Telnyx: verify telnyx-signature header
- LiveKit: verify livekit-signature header
NEVER process a webhook without verifying the signature first.

---

## Endpoint Structure

Order of operations for every endpoint:
1. Auth dependency (get_current_user or get_api_key)
2. Permission check — role check BEFORE any DB operation
3. Tenant isolation — filter by org_id
4. Business logic
5. Audit log (on all write operations)
6. Return response model

Example endpoint:

@router.post("/agents", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ["admin", "sales"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if agent_data.org_id != current_user.org_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Cannot create agent for another org")

    agent = Agent(**agent_data.dict())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    await audit_log(db, current_user.id, "created", "agent", agent.id)

    return agent

---

## Response Format

Single resource:
Return Pydantic response model directly.

Lists:
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
}

Errors:
{"detail": "message"} via HTTPException
Never return raw exception traces or stack traces.

---

## Status Codes

- 200: success (GET, PUT)
- 201: created (POST)
- 204: deleted (DELETE, no content returned)
- 400: bad request (invalid input not caught by Pydantic)
- 401: unauthorized (no session, invalid API key)
- 403: forbidden (valid auth but insufficient permissions)
- 404: not found (resource doesn't exist or wrong org)
- 422: validation error (Pydantic handles automatically)
- 502: external service error (xAI, Telnyx, LiveKit failure)

---

## Tenant Isolation

EVERY org-scoped query MUST filter by org_id.
A 404 is correct when a resource exists but belongs to another org.
Never return 403 in a way that confirms the resource exists.

---

## Roles and Permissions

Admin (John):
- Full access to everything
- Can query across org boundaries on admin endpoints

Sales (Hugh):
- Manage clients and agents
- Cannot access billing internals

Cold Caller:
- LMS access only
- No dashboard or API access

Client:
- View own org data only
- Cannot modify agents directly

---

## Router Organization

app/api/routers/
- auth.py — login, logout, session, api-keys
- organizations.py — org CRUD
- agents.py — agent CRUD
- phone_numbers.py — number provisioning
- knowledge_base.py — xAI Collections management
- call_logs.py — call history and transcripts
- webhooks.py — Stripe, Telnyx, LiveKit, call-outcome

All routers registered in app/api/__init__.py with appropriate prefixes and tags.

---

## External Service Errors

When xAI, Telnyx, or LiveKit calls fail:
- Log the full error internally
- Return 502 to the client with a generic message
- Never expose external service error details to clients

try:
    result = await xai_client.query_collection(...)
except Exception as e:
    logger.error(f"xAI Collections error: {e}")
    raise HTTPException(status_code=502, detail="Knowledge base temporarily unavailable")

---

## Webhook Handlers

All webhook handlers must:
1. Verify signature FIRST — return 400 immediately if invalid
2. Return 200 quickly — do heavy processing in background via ARQ
3. Be idempotent — safe to receive same event twice
4. Log every received webhook for debugging

Pattern:

@router.post("/webhooks/telnyx")
async def telnyx_webhook(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get("telnyx-signature-ed25519")
    if not verify_telnyx_signature(signature, await request.body()):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    background_tasks.add_task(process_telnyx_event, payload)

    return {"status": "received"}
