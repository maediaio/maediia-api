"""Telnyx service — phone number provisioning, SMS sending, webhook verification.

The telnyx library (v2.1.3) is synchronous. All calls are wrapped with
asyncio.to_thread() to avoid blocking the event loop.

Number lifecycle:
  search_numbers()   → available numbers to show in UI
  purchase_number()  → buy + assign to SIP connection, returns telnyx_number_id
  release_number()   → cancel number from Telnyx

SMS:
  send_sms()         → send via Telnyx Messaging API (sms_opt_out check is caller's responsibility)

Webhook:
  verify_signature() → Ed25519 verification using WebhookSignature.verify
"""
import asyncio
import logging
from typing import Any

import telnyx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


def _configure() -> None:
    """Set Telnyx API key from settings."""
    telnyx.api_key = settings.TELNYX_API_KEY


# ---------------------------------------------------------------------------
# Number search
# ---------------------------------------------------------------------------

async def search_numbers(
    country_code: str = "US",
    area_code: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search available phone numbers from Telnyx.

    Returns:
        List of dicts with keys: number, region, locality, features
    """
    _configure()

    def _search():
        params: dict[str, Any] = {
            "filter[country_code]": country_code,
            "filter[limit]": limit,
        }
        if area_code:
            params["filter[national_destination_code]"] = area_code

        response = telnyx.AvailablePhoneNumber.list(**params)
        results = []
        for item in response.data:
            results.append({
                "number": item.phone_number,
                "region": getattr(item, "region_information", [{}])[0].get("region_name", "") if getattr(item, "region_information", None) else "",
                "locality": getattr(item, "locality", ""),
                "features": getattr(item, "features", []),
            })
        return results

    try:
        return await asyncio.to_thread(_search)
    except telnyx.error.TelnyxError as e:
        logger.error("Telnyx search_numbers error: %s", e)
        raise HTTPException(status_code=502, detail="Phone number search unavailable")


# ---------------------------------------------------------------------------
# Number provisioning
# ---------------------------------------------------------------------------

async def purchase_number(phone_number: str) -> str:
    """
    Purchase a phone number from Telnyx and assign it to the SIP connection.

    Args:
        phone_number: E.164 number selected from search results

    Returns:
        telnyx_number_id — the Telnyx resource ID for this number (stored in DB)
    """
    _configure()

    def _purchase():
        order = telnyx.NumberOrder.create(
            phone_numbers=[{"phone_number": phone_number}],
            connection_id=settings.TELNYX_SIP_CONNECTION_ID or None,
        )
        # NumberOrder.phone_numbers[0].id is the Telnyx number resource ID
        return order.phone_numbers[0].id

    try:
        return await asyncio.to_thread(_purchase)
    except telnyx.error.TelnyxError as e:
        logger.error("Telnyx purchase_number error (%s): %s", phone_number, e)
        raise HTTPException(status_code=502, detail="Phone number provisioning unavailable")


async def release_number(telnyx_number_id: str) -> None:
    """
    Release (delete) a phone number back to Telnyx.

    Args:
        telnyx_number_id: The Telnyx resource ID stored in PhoneNumber.telnyx_connection_id
                          or BusinessLine.telnyx_number_id
    """
    _configure()

    def _release():
        telnyx.PhoneNumber.delete(telnyx_number_id)

    try:
        await asyncio.to_thread(_release)
        logger.info("Released Telnyx number %s", telnyx_number_id)
    except telnyx.error.TelnyxError as e:
        logger.error("Telnyx release_number error (%s): %s", telnyx_number_id, e)
        raise HTTPException(status_code=502, detail="Phone number release unavailable")


# ---------------------------------------------------------------------------
# SMS
# ---------------------------------------------------------------------------

async def send_sms(from_number: str, to_number: str, message: str) -> str:
    """
    Send an SMS via Telnyx Messaging API.

    NOTE: Caller is responsible for checking sms_opt_out before calling this.

    Args:
        from_number: Sending number in E.164 format (must be a Telnyx-provisioned number)
        to_number: Recipient number in E.164 format
        message: SMS body text

    Returns:
        Telnyx message ID
    """
    _configure()

    def _send():
        msg = telnyx.Message.create(
            from_=from_number,
            to=to_number,
            text=message,
        )
        return msg.id

    try:
        message_id = await asyncio.to_thread(_send)
        logger.info("SMS sent: from=%s to=%s id=%s", from_number, to_number, message_id)
        return message_id
    except telnyx.error.TelnyxError as e:
        logger.error("Telnyx send_sms error (to=%s): %s", to_number, e)
        raise HTTPException(status_code=502, detail="SMS service unavailable")


# ---------------------------------------------------------------------------
# Webhook signature verification
# ---------------------------------------------------------------------------

def verify_signature(body: bytes, signature: str, timestamp: str) -> bool:
    """
    Verify a Telnyx webhook signature (Ed25519).

    Args:
        body: Raw request body bytes
        signature: Value of telnyx-signature-ed25519 header
        timestamp: Value of telnyx-timestamp header

    Returns:
        True if valid, False otherwise
    """
    if not settings.TELNYX_WEBHOOK_SECRET:
        return False
    try:
        telnyx.WebhookSignature.verify(
            payload=body,
            signature=signature,
            timestamp=timestamp,
            tolerance=300,  # 5-minute tolerance
        )
        return True
    except Exception:
        return False
