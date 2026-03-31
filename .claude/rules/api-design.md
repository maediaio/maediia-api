# API Design Rules

## Endpoint Reference
Full endpoint list: @docs/PLATFORM_ARCHITECTURE.md Section 4

## Auth
- Every endpoint has Depends(get_current_user) OR Depends(get_api_key)
- Exceptions: /auth/login, /auth/password/reset, webhooks, public review pages
- Webhooks use signature verification (Stripe, Telnyx, LiveKit)
- Permission check FIRST before any DB operation

## Response Format
- Success: return Pydantic response model directly
- Lists: { items: [...], total: int, page: int, page_size: int }
- Errors: { detail: "message" } via HTTPException

## Tenant Isolation
- EVERY org-scoped query MUST filter by org_id
- Admin role bypasses for admin endpoints only

## Status Codes
200 success, 201 created, 204 deleted, 400 bad request, 401 unauthorized, 403 forbidden, 404 not found, 422 validation error, 502 external service error
