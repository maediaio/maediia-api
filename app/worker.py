"""ARQ worker — run with: python -m arq app.worker.WorkerSettings

This is the background task worker process. It runs independently of the
FastAPI app, connects to the same Redis and PostgreSQL instances, and
executes all enqueued task functions.
"""
import logging
from urllib.parse import urlparse

from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.tasks.sms import send_sms
from app.tasks.reminders import send_appointment_reminder

logger = logging.getLogger(__name__)


def _redis_settings() -> RedisSettings:
    """Parse REDIS_URL into ARQ RedisSettings."""
    url = urlparse(settings.REDIS_URL)
    return RedisSettings(
        host=url.hostname or "localhost",
        port=url.port or 6379,
        password=url.password or None,
        database=int(url.path.lstrip("/") or 0),
    )


async def startup(ctx: dict) -> None:
    """
    Initialize resources shared across all task executions in this worker process.
    Injects into ctx so task functions can access them.
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    ctx["engine"] = engine
    ctx["db"] = session_factory
    logger.info("ARQ worker started — DB pool ready")


async def shutdown(ctx: dict) -> None:
    """Dispose DB engine on worker shutdown."""
    engine = ctx.get("engine")
    if engine:
        await engine.dispose()
    logger.info("ARQ worker shut down")


class WorkerSettings:
    """ARQ worker configuration."""

    redis_settings = _redis_settings()

    functions = [
        send_sms,
        send_appointment_reminder,
    ]

    on_startup = startup
    on_shutdown = shutdown

    # Worker concurrency and timeouts
    max_jobs = 10
    job_timeout = 300       # 5 minutes max per job
    keep_result = 3600      # keep job results in Redis for 1 hour
    retry_jobs = True
    max_tries = 3
