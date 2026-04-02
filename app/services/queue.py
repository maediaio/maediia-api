"""Task queue service — enqueue ARQ jobs and persist ScheduledTask records.

Usage:
    from app.services.queue import enqueue
    from datetime import datetime, timedelta

    # Immediate
    await enqueue(db, org_id, "send_sms", to_number="+15555551234", message="Hi")

    # Deferred
    run_at = datetime.utcnow() + timedelta(hours=24)
    await enqueue(db, org_id, "send_appointment_reminder", run_at=run_at, ...)
"""
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scheduled_task import ScheduledTask
from app.services.redis import get_arq_pool

logger = logging.getLogger(__name__)


async def enqueue(
    db: AsyncSession,
    org_id: UUID,
    task_name: str,
    run_at: datetime | None = None,
    **kwargs,
) -> ScheduledTask:
    """
    Persist a ScheduledTask record and enqueue it with ARQ.

    Args:
        db: AsyncSession — caller is responsible for commit
        org_id: Organization this task belongs to
        task_name: ARQ function name (e.g. "send_sms", "send_appointment_reminder")
        run_at: Optional future datetime for deferred execution (UTC).
                None = enqueue immediately.
        **kwargs: Arguments forwarded to the task function

    Returns:
        The persisted ScheduledTask record (status="pending")
    """
    task = ScheduledTask(
        org_id=org_id,
        task_name=task_name,
        kwargs=kwargs,
        enqueue_at=run_at,
        status="pending",
    )
    db.add(task)
    await db.flush()  # get task.id before enqueuing

    arq_kwargs: dict = {"task_id": str(task.id), **kwargs}
    pool = get_arq_pool()

    if run_at:
        job = await pool.enqueue_job(task_name, _defer_until=run_at, **arq_kwargs)
    else:
        job = await pool.enqueue_job(task_name, **arq_kwargs)

    if job:
        task.arq_job_id = job.job_id
    else:
        # ARQ returns None if a job with this ID already exists (dedup)
        logger.warning("enqueue: ARQ returned None for task %s — possible duplicate", task_name)
        task.status = "duplicate"

    return task
