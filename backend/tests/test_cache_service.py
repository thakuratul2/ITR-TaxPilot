"""Tests for Redis and in-memory CacheService."""

import pytest

from app.cache.cache_service import CacheService


@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Test basic cache set and get operations."""
    test_key = "test:unit:key1"
    test_value = {"status": "ok", "count": 42, "items": ["a", "b"]}

    success = await CacheService.set(test_key, test_value, ttl_seconds=60)
    assert success is True

    cached = await CacheService.get(test_key)
    assert cached is not None
    assert cached["status"] == "ok"
    assert cached["count"] == 42
    assert cached["items"] == ["a", "b"]


@pytest.mark.asyncio
async def test_cache_delete():
    """Test deleting keys from cache."""
    test_key = "test:unit:key2"
    await CacheService.set(test_key, {"temp": True}, ttl_seconds=60)

    deleted = await CacheService.delete(test_key)
    assert deleted is True

    cached = await CacheService.get(test_key)
    assert cached is None


@pytest.mark.asyncio
async def test_cache_job_state():
    """Test job state caching helper."""
    job_id = "test-job-uuid-caching"
    job_payload = {
        "job_id": job_id,
        "status": "calculating",
        "progress_percentage": 75,
        "step_description": "Computing tax liability",
    }

    await CacheService.cache_job_state(job_id, job_payload)
    retrieved = await CacheService.get_cached_job_state(job_id)

    assert retrieved is not None
    assert retrieved["job_id"] == job_id
    assert retrieved["status"] == "calculating"
    assert retrieved["progress_percentage"] == 75


@pytest.mark.asyncio
async def test_cache_result_and_ttl():
    """Test calculation result caching with TTL."""
    result_id = "doc-res-123"
    result_data = {
        "document_id": result_id,
        "tax_payable": 15000.0,
        "recommended_regime": "NEW",
    }

    await CacheService.cache_result(result_id, result_data, ttl_seconds=120)
    retrieved = await CacheService.get_cached_result(result_id)

    assert retrieved is not None
    assert retrieved["tax_payable"] == 15000.0
    assert retrieved["recommended_regime"] == "NEW"
