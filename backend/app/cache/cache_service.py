"""Redis caching service with configurable TTL and in-memory fallback."""

import json
import logging
from typing import Any

from app.cache.redis import get_redis_client
from app.core.config import get_settings

logger = logging.getLogger("app.cache.service")

# In-memory store fallback when Redis is unreachable or for isolated unit tests
_in_memory_cache: dict[str, tuple[str, float | None]] = {}


class CacheService:
    """Centralized caching service supporting TTL, JSON serialization, and fallback."""

    JOB_PREFIX = "taxpilot:job:"
    RESULT_PREFIX = "taxpilot:result:"
    RATE_LIMIT_PREFIX = "taxpilot:ratelimit:"

    @classmethod
    async def set(cls, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """Store serialized value under key with optional TTL."""
        settings = get_settings()
        ttl = ttl_seconds if ttl_seconds is not None else settings.RESULT_CACHE_TTL_SECONDS
        serialized = json.dumps(value, default=str)

        try:
            client = await get_redis_client()
            if client is not None:
                if ttl > 0:
                    await client.set(key, serialized, ex=ttl)
                else:
                    await client.set(key, serialized)
                return True
        except Exception as e:
            logger.debug("Redis set failed for key %s, using in-memory store: %s", key, e)

        # Fallback to in-memory cache
        import time
        expires_at = time.time() + ttl if ttl and ttl > 0 else None
        _in_memory_cache[key] = (serialized, expires_at)
        return True

    @classmethod
    async def get(cls, key: str) -> Any | None:
        """Retrieve and deserialize value by key."""
        try:
            client = await get_redis_client()
            if client is not None:
                data = await client.get(key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.debug("Redis get failed for key %s, checking in-memory store: %s", key, e)

        # Check in-memory cache fallback
        import time
        if key in _in_memory_cache:
            serialized, expires_at = _in_memory_cache[key]
            if expires_at is None or expires_at > time.time():
                try:
                    return json.loads(serialized)
                except Exception:
                    return None
            else:
                del _in_memory_cache[key]

        return None

    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete key from cache."""
        try:
            client = await get_redis_client()
            if client is not None:
                await client.delete(key)
        except Exception as e:
            logger.debug("Redis delete failed for key %s: %s", key, e)

        if key in _in_memory_cache:
            del _in_memory_cache[key]
        return True

    @classmethod
    async def cache_job_state(cls, job_id: str, data: dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Cache current job processing state and progress."""
        key = f"{cls.JOB_PREFIX}{job_id}"
        return await cls.set(key, data, ttl_seconds=ttl_seconds)

    @classmethod
    async def get_cached_job_state(cls, job_id: str) -> dict[str, Any] | None:
        """Fetch cached job state by ID."""
        key = f"{cls.JOB_PREFIX}{job_id}"
        return await cls.get(key)

    @classmethod
    async def cache_result(cls, result_id: str, result_data: dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Cache tax computation or document analysis result."""
        key = f"{cls.RESULT_PREFIX}{result_id}"
        return await cls.set(key, result_data, ttl_seconds=ttl_seconds)

    @classmethod
    async def get_cached_result(cls, result_id: str) -> dict[str, Any] | None:
        """Fetch cached analysis or calculation result."""
        key = f"{cls.RESULT_PREFIX}{result_id}"
        return await cls.get(key)

    @classmethod
    def clear_in_memory_cache(cls) -> None:
        """Clear fallback cache (useful in tests)."""
        _in_memory_cache.clear()
