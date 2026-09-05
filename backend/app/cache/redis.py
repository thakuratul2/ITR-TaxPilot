"""Redis connection manager and health check utilities."""

import logging

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger("app.cache.redis")

_redis_client: Redis | None = None


async def get_redis_client() -> Redis | None:
    """Get or initialize singleton async Redis client."""
    global _redis_client

    if _redis_client is not None:
        try:
            pool = getattr(_redis_client, "connection_pool", None)
            loop = getattr(pool, "_loop", None) if pool else None
            if loop is not None and loop.is_closed():
                _redis_client = None
        except Exception:
            _redis_client = None

    if _redis_client is None:
        settings = get_settings()
        try:
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
            )
        except Exception as e:
            logger.warning("Failed to initialize Redis client: %s", str(e))
            return None
    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client connection gracefully."""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.aclose()
        except Exception:
            pass
        finally:
            _redis_client = None


async def check_redis_health() -> bool:
    """Check Redis server health via ping with fast timeout."""
    import asyncio
    client = await get_redis_client()
    if client is None:
        return False
    try:
        response = await asyncio.wait_for(client.ping(), timeout=0.5)
        return response is True
    except Exception:
        return False
