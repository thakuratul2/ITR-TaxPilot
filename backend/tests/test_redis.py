"""Tests for Redis client and connection manager."""

import pytest

from app.cache.redis import check_redis_health, close_redis_client, get_redis_client


@pytest.mark.asyncio
async def test_redis_client_lifecycle():
    """Test obtaining and closing Redis client."""
    client = await get_redis_client()
    assert client is not None
    await close_redis_client()


@pytest.mark.asyncio
async def test_redis_health_check_fallback():
    """Test health check returns boolean without raising unhandled exception."""
    health = await check_redis_health()
    assert isinstance(health, bool)
    await close_redis_client()
