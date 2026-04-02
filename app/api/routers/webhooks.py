"""Webhooks router — Stripe, Telnyx, LiveKit, call-outcome.

All webhook endpoints verify provider signatures before processing.
Heavy processing is offloaded to background tasks (ARQ queue).
"""
import logging
from typing import Any, Dict

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_api_key
from app.db.session import AsyncSessionLocal, get_db
from app.models.api_key import ApiKey

logger = logging.getLogger(__name__)
router = APIRouter()


def _verify_telnyx_signature(signature: str | None, timestamp: str | None, body: bytes) -> bool:
    """Verify Telnyx webhook signature (Ed25519)."""
    if not signature or not timestamp:
        return False
    from app.services.telnyx_service import verify_signature
    return verify_signature(body=body, signature=signature, timestamp=timestamp)


def _verify_livekit_signature(signature: str | None, body: bytes) -> bool:
    """Verify LiveKit webhook signature (JWT). Stub until LIVEKIT_API_SECRET is set."""
    if not settings.LIVEKIT_API_SECRET:
        return False
    # TODO (Part 1): implement JWT verification using livekit_api library
    return False


def _parse_stripe_event(signature: str | None, body: bytes) -> stripe.Event:
    """
    Verify Stripe webhook signature and parse the event.
    Raises HTTPException(400) if signature is invalid or secret not configured.
    """
    if not settings.STRIPE_WEBHOOK_SECRET or not signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
    try:
        return stripe.Webhook.construct_event(
            payload=body,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")


@router.post("/webhooks/telnyx")
async def telnyx_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    body = await request.body()
    signature = request.headers.get("telnyx-signature-ed25519")
    timestamp = request.headers.get("telnyx-timestamp")

    if not _verify_telnyx_signature(signature, timestamp, body):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload: Dict[str, Any] = await request.json()
    background_tasks.add_task(_process_telnyx_event, payload)
    return {"status": "received"}


@router.post("/webhooks/livekit")
async def livekit_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    body = await request.body()
    signature = request.headers.get("authorization")

    if not _verify_livekit_signature(signature, body):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload: Dict[str, Any] = await request.json()
    background_tasks.add_task(_process_livekit_event, payload)
    return {"status": "received"}


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    body = await request.body()
    signature = request.headers.get("stripe-signature")
    event = _parse_stripe_event(signature, body)
    background_tasks.add_task(_process_stripe_event, event)
    return {"status": "received"}


@router.post("/webhooks/call-outcome")
async def call_outcome_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives call outcome from agent worker after call ends.
    Triggers post-call automation: SMS, scheduled follow-ups via ARQ.
    Auth: API key (agent worker sends this after every call).
    """
    raw_key = request.headers.get("x-api-key")
    if not raw_key:
        raise HTTPException(status_code=401, detail="API key required")

    hashed = hash_api_key(raw_key)
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == hashed, ApiKey.is_active == True)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=401, detail="Invalid API key")

    payload: Dict[str, Any] = await request.json()
    background_tasks.add_task(_process_call_outcome, payload)
    return {"status": "received"}


async def _process_telnyx_event(payload: Dict[str, Any]) -> None:
    """
    Process Telnyx webhook events.

    Handled events:
    - call.initiated / call.answered / call.hangup  → logged (full handling in Part 1)
    - messaging.message.sent                         → logged
    - messaging.message.failed                       → logged as warning
    """
    data = payload.get("data", {})
    event_type: str = data.get("event_type", "unknown")
    event_id: str = data.get("id", "")
    logger.info("Telnyx event: %s id=%s", event_type, event_id)

    if event_type in ("call.initiated", "call.answered", "call.hangup"):
        # Full call event handling implemented in Part 1 (Voice POC)
        call_payload = data.get("payload", {})
        logger.info(
            "Telnyx call event %s: call_leg=%s from=%s to=%s",
            event_type,
            call_payload.get("call_leg_id", ""),
            call_payload.get("from", ""),
            call_payload.get("to", ""),
        )

    elif event_type == "messaging.message.sent":
        msg_payload = data.get("payload", {})
        logger.info(
            "Telnyx SMS sent: id=%s to=%s",
            msg_payload.get("id", ""),
            msg_payload.get("to", [{}])[0].get("phone_number", "") if msg_payload.get("to") else "",
        )

    elif event_type == "messaging.message.failed":
        msg_payload = data.get("payload", {})
        logger.warning(
            "Telnyx SMS failed: id=%s errors=%s",
            msg_payload.get("id", ""),
            msg_payload.get("errors", []),
        )


async def _process_livekit_event(payload: Dict[str, Any]) -> None:
    """Process LiveKit events in background. Implemented in Part 1 (Voice POC)."""
    # TODO: handle room_started, room_finished, participant_joined, etc.


async def _process_stripe_event(event: stripe.Event) -> None:
    """
    Handle Stripe webhook events — subscription lifecycle + payment status.

    Handled events:
    - customer.subscription.created / updated  → sync plan + subscription ID to org
    - customer.subscription.deleted            → downgrade org to 'starter', clear subscription ID
    - invoice.payment_failed                   → log warning (future: send alert)
    """
    from app.models.organization import Organization

    event_type: str = event.type
    logger.info("Stripe event: %s id=%s", event_type, event.id)

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        subscription = event.data.object
        customer_id: str = subscription.customer
        plan = _plan_from_subscription(subscription)

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Organization).where(
                        Organization.stripe_customer_id == customer_id
                    )
                )
                org = result.scalar_one_or_none()
                if org:
                    org.plan = plan
                    org.stripe_subscription_id = subscription.id
                    await db.commit()
                    logger.info("Updated org %s plan=%s subscription=%s", org.id, plan, subscription.id)
                else:
                    logger.warning("Stripe subscription event for unknown customer %s", customer_id)
        except Exception:
            logger.error("Failed to process Stripe %s for customer %s", event_type, customer_id, exc_info=True)

    elif event_type == "customer.subscription.deleted":
        subscription = event.data.object
        customer_id = subscription.customer

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Organization).where(
                        Organization.stripe_customer_id == customer_id
                    )
                )
                org = result.scalar_one_or_none()
                if org:
                    org.plan = "starter"
                    org.stripe_subscription_id = None
                    await db.commit()
                    logger.info("Subscription deleted — org %s downgraded to starter", org.id)
        except Exception:
            logger.error("Failed to process Stripe subscription.deleted for customer %s", customer_id, exc_info=True)

    elif event_type == "invoice.payment_failed":
        invoice = event.data.object
        logger.warning(
            "Invoice payment failed: customer=%s invoice=%s amount=%s",
            invoice.customer,
            invoice.id,
            invoice.amount_due,
        )
        # Future: send email alert or flag org for follow-up


def _plan_from_subscription(subscription: Any) -> str:
    """
    Derive plan name from a Stripe subscription's metadata or price nickname.
    Falls back to 'starter' if unrecognised.
    """
    # Prefer metadata set on the subscription itself
    if subscription.metadata and subscription.metadata.get("plan"):
        return subscription.metadata["plan"]
    # Fall back to price nickname
    if subscription.items and subscription.items.data:
        nickname = subscription.items.data[0].price.nickname
        if nickname:
            return nickname.lower()
    return "starter"


async def _process_call_outcome(payload: Dict[str, Any]) -> None:
    """Trigger post-call automation. Implemented in Step 3 (ARQ worker)."""
    # TODO: evaluate agent's post_call_rules, enqueue SMS/reminder tasks in ARQ
