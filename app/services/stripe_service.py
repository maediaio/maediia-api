"""Stripe service — customer and subscription management.

All calls use stripe.AsyncStripe for non-blocking I/O.
On external failure, raises HTTPException(502) so the caller gets a clean error.

Plan → Stripe price ID mapping is driven by STRIPE_PRICE_* env vars so price IDs
never need to be redeployed if Stripe products are recreated.
"""
import logging
from uuid import UUID

import stripe
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


def _client() -> stripe.StripeClient:
    """Return a configured Stripe client."""
    return stripe.StripeClient(api_key=settings.STRIPE_SECRET_KEY)


async def create_customer(org_id: UUID, org_name: str, email: str | None = None) -> str:
    """
    Create a Stripe customer for an organization.

    Args:
        org_id: Organization UUID — stored as customer metadata for webhook lookups
        org_name: Display name on the Stripe customer
        email: Billing email (optional)

    Returns:
        Stripe customer ID (cus_...)
    """
    try:
        client = _client()
        customer = await client.customers.create_async(
            params={
                "name": org_name,
                "email": email,
                "metadata": {"org_id": str(org_id)},
            }
        )
        logger.info("Created Stripe customer %s for org %s", customer.id, org_id)
        return customer.id
    except stripe.StripeError as e:
        logger.error("Stripe create_customer error: %s", e)
        raise HTTPException(status_code=502, detail="Billing service unavailable")


async def create_subscription(customer_id: str, price_id: str) -> dict:
    """
    Create a Stripe subscription for a customer.

    Args:
        customer_id: Stripe customer ID (cus_...)
        price_id: Stripe price ID (price_...) for the plan being subscribed to

    Returns:
        {"subscription_id": "sub_...", "status": "active"|"trialing"|...}
    """
    try:
        client = _client()
        subscription = await client.subscriptions.create_async(
            params={
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"],
            }
        )
        logger.info("Created subscription %s for customer %s", subscription.id, customer_id)
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
        }
    except stripe.StripeError as e:
        logger.error("Stripe create_subscription error: %s", e)
        raise HTTPException(status_code=502, detail="Billing service unavailable")


async def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> dict:
    """
    Cancel a Stripe subscription.

    Args:
        subscription_id: Stripe subscription ID (sub_...)
        at_period_end: If True (default), access continues until the billing period ends.
                       If False, cancels immediately.

    Returns:
        {"subscription_id": "sub_...", "status": "canceled"|"active", "cancel_at_period_end": bool}
    """
    try:
        client = _client()
        if at_period_end:
            subscription = await client.subscriptions.update_async(
                subscription_id,
                params={"cancel_at_period_end": True},
            )
        else:
            subscription = await client.subscriptions.cancel_async(subscription_id)
        logger.info("Cancelled subscription %s (at_period_end=%s)", subscription_id, at_period_end)
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
        }
    except stripe.StripeError as e:
        logger.error("Stripe cancel_subscription error: %s", e)
        raise HTTPException(status_code=502, detail="Billing service unavailable")


async def get_subscription(subscription_id: str) -> dict:
    """
    Fetch current subscription details.

    Returns:
        {"subscription_id": ..., "status": ..., "plan": ..., "current_period_end": ...}
    """
    try:
        client = _client()
        sub = await client.subscriptions.retrieve_async(subscription_id)
        price_id = sub.items.data[0].price.id if sub.items.data else None
        return {
            "subscription_id": sub.id,
            "status": sub.status,
            "price_id": price_id,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
        }
    except stripe.StripeError as e:
        logger.error("Stripe get_subscription error: %s", e)
        raise HTTPException(status_code=502, detail="Billing service unavailable")
