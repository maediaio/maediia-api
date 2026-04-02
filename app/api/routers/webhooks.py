"""Webhooks router — Stripe, Telnyx, LiveKit, call-outcome.

All webhook endpoints verify provider signatures before processing.
Heavy processing is offloaded to background tasks (ARQ queue in Step 3).
"""
import hashlib
import hmac
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


def _verify_telnyx_signature(signature: str | None, body: bytes) -> bool:
    """Verify Telnyx webhook signature (Ed25519). Stub until TELNYX_WEBHOOK_SECRET is set."""
    if not settings.TELNYX_WEBHOOK_SECRET:
        return False
    # TODO: implement Ed25519 verification using telnyx SDK or cryptography library
    return False


def _verify_livekit_signature(signature: str | None, body: bytes) -> bool:
    """Verify LiveKit webhook signature (JWT). Stub until LIVEKIT_API_SECRET is set."""
    if not settings.LIVEKIT_API_SECRET:
        return False
    # TODO: implement JWT verification using livekit_api library
    return False


def _verify_stripe_signature(signature: str | None, body: bytes) -> bool:
    """Verify Stripe webhook signature (HMAC-SHA256)."""
    if not settings.STRIPE_WEBHOOK_SECRET or not signature:
        return False
    # TODO: use stripe.WebhookSignature.verify_header()
    return False


@router.post("/webhooks/telnyx")
async def telnyx_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    body = await request.body()
    signature = request.headers.get("telnyx-signature-ed25519")

    if not _verify_telnyx_signature(signature, body):
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

    if not _verify_stripe_signature(signature, body):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload: Dict[str, Any] = await request.json()
    background_tasks.add_task(_process_stripe_event, payload)
    return {"status": "received"}


@router.post("/webhooks/call-outcome")
async def call_outcome_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Receives call outcome from agent worker after call ends.
    Triggers post-call automation: SMS, scheduled follow-ups via ARQ.
    Auth: API key (agent worker sends this after every call).
    """
    # Verify X-API-Key header
    api_key_header = request.headers.get("x-api-key")
    if not api_key_header:
        raise HTTPException(status_code=401, detail="API key required")

    # Full API key validation done in Step 3 when ARQ worker is built.
    # For now, verify the key is non-empty and well-formed.
    if not api_key_header.startswith("mk_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    payload: Dict[str, Any] = await request.json()
    background_tasks.add_task(_process_call_outcome, payload)
    return {"status": "received"}


async def _process_telnyx_event(payload: Dict[str, Any]) -> None:
    """Process Telnyx events in background. Implemented in Step 5 (Telnyx integration)."""
    event_type = payload.get("data", {}).get("event_type", "unknown")
    # TODO: handle call.initiated, call.answered, call.hangup, message.sent etc.


async def _process_livekit_event(payload: Dict[str, Any]) -> None:
    """Process LiveKit events in background. Implemented in Part 1 (Voice POC)."""
    # TODO: handle room_started, room_finished, participant_joined, etc.


async def _process_stripe_event(payload: Dict[str, Any]) -> None:
    """Process Stripe events in background. Implemented in Step 4 (Stripe integration)."""
    event_type = payload.get("type", "unknown")
    # TODO: handle customer.subscription.created, invoice.paid, etc.


async def _process_call_outcome(payload: Dict[str, Any]) -> None:
    """Trigger post-call automation. Implemented in Step 3 (ARQ worker)."""
    # TODO: evaluate agent's post_call_rules, enqueue SMS/reminder tasks in ARQ
