"""Appointment reminder task — sends SMS reminder before a scheduled appointment.

Enqueued with a future `_defer_until` by the voice post-call automation.
Wired to Telnyx in Phase 0 Step 5.
"""
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


async def send_appointment_reminder(
    ctx: dict,
    org_id: str,
    appointment_id: str,
    from_number: str,
    to_number: str,
    message: str,
    task_id: str | None = None,
) -> dict:
    """
    Send an appointment reminder SMS.

    Args:
        ctx: ARQ context
        org_id: Organization UUID string
        appointment_id: Appointment UUID string (for logging/dedup)
        from_number: Telnyx-provisioned sender number in E.164 format
        to_number: Recipient phone number in E.164 format
        message: Reminder message body
        task_id: ScheduledTask.id to update status on completion

    Returns:
        {"status": "sent", "appointment_id": appointment_id}
    """
    logger.info(
        "send_appointment_reminder: appointment=%s to=%s org=%s",
        appointment_id, to_number, org_id,
    )

    # Delegates to send_sms — both use Telnyx under the hood
    from app.tasks.sms import send_sms
    result = await send_sms(
        ctx,
        org_id=org_id,
        from_number=from_number,
        to_number=to_number,
        message=message,
        task_id=task_id,
    )

    return {"status": result["status"], "appointment_id": appointment_id}
