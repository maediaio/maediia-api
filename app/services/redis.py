"""Redis connection pool — shared async client for the application."""
from redis.asyncio import Redis, ConnectionPool
from arq import create_pool as arq_create_pool
from arq.connections import ArqRedis, RedisSettings as ArqRedisSettings
from app.core.config import settings

# Module-level pool — initialized on app startup, closed on shutdown
_pool: ConnectionPool | None = None
_client: Redis | None = None
_arq_pool: ArqRedis | None = None


def _parse_arq_settings() -> ArqRedisSettings:
    """Parse REDIS_URL into arq RedisSettings."""
    from urllib.parse import urlparse
    url = urlparse(settings.REDIS_URL)
    return ArqRedisSettings(
        host=url.hostname or "localhost",
        port=url.port or 6379,
        password=url.password or None,
        database=int(url.path.lstrip("/") or 0),
    )


async def connect() -> None:
    """Create the Redis connection pool and ARQ pool. Call on application startup."""
    global _pool, _client, _arq_pool
    _pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        decode_responses=True,
    )
    _client = Redis(connection_pool=_pool)
    _arq_pool = await arq_create_pool(_parse_arq_settings())


async def disconnect() -> None:
    """Close all Redis connections. Call on application shutdown."""
    global _pool, _client, _arq_pool
    if _arq_pool:
        await _arq_pool.aclose()
        _arq_pool = None
    if _client:
        await _client.aclose()
        _client = None
    if _pool:
        await _pool.aclose()
        _pool = None


def get_client() -> Redis:
    """Return the active Redis client. Raises if not connected."""
    if _client is None:
        raise RuntimeError("Redis is not connected. Call connect() first.")
    return _client


def get_arq_pool() -> ArqRedis:
    """Return the active ARQ pool. Raises if not connected."""
    if _arq_pool is None:
        raise RuntimeError("ARQ pool is not connected. Call connect() first.")
    return _arq_pool
