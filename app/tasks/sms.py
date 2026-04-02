"""SMS task — post-call and reminder SMS via Telnyx."""
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


async def send_sms(
    ctx: dict,
    org_id: str,
    from_number: str,
    to_number: str,
    message: str,
    task_id: str | None = None,
) -> dict:
    """
    Send an SMS via Telnyx Messaging API.

    Args:
        ctx: ARQ context
        org_id: Organization UUID string (for logging/audit)
        from_number: Telnyx-provisioned sender number in E.164 format
        to_number: Recipient phone number in E.164 format
        message: SMS body text
        task_id: ScheduledTask.id to update on completion

    Returns:
        {"status": "sent", "message_id": "..."}
    """
    from app.services.telnyx_service import send_sms as telnyx_send

    logger.info("send_sms task: from=%s to=%s org=%s", from_number, to_number, org_id)
    message_id = await telnyx_send(from_number=from_number, to_number=to_number, message=message)

    if task_id:
        await _mark_complete(ctx, task_id, {"message_id": message_id})

    return {"status": "sent", "message_id": message_id}


async def _mark_complete(ctx: dict, task_id: str, result: dict) -> None:
    """Update ScheduledTask status to 'complete' with result payload."""
    from app.models.scheduled_task import ScheduledTask

    try:
        async with ctx["db"]() as session:
            row = await session.get(ScheduledTask, UUID(task_id))
            if row:
                row.status = "complete"
                row.result = result
                await session.commit()
    except Exception:
        logger.warning("Failed to mark task %s complete — result not persisted", task_id, exc_info=True)
