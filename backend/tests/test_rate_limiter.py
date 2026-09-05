import uuid

from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_rate_limiter_headers_present(client: TestClient):
    """Test rate limit headers are included in responses."""
    response = client.get("/api/v1/auth/me", headers={"X-Forwarded-For": f"10.0.1.{uuid.uuid4().hex[:4]}"})
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


def test_rate_limiter_exempt_paths(client: TestClient):
    """Test exempt paths like /health are not rate limited."""
    response = client.get("/health")
    assert response.status_code == 200


def test_rate_limiter_blocks_burst(client: TestClient):
    """Test rate limiting triggers 429 when threshold exceeded."""
    app_settings = getattr(client.app.state, "settings", None) or get_settings()
    original_limit = app_settings.RATE_LIMIT_PER_MINUTE
    unique_ip = f"192.168.200.{uuid.uuid4().hex[:6]}"
    test_headers = {"X-Forwarded-For": unique_ip}
    try:
        # Lower limit temporarily for test
        app_settings.RATE_LIMIT_PER_MINUTE = 3

        # First 3 requests should pass
        for _ in range(3):
            res = client.get("/api/v1/admin/ai-providers", headers=test_headers)
            assert res.status_code == 200

        # 4th request should exceed limit
        res_blocked = client.get("/api/v1/admin/ai-providers", headers=test_headers)
        assert res_blocked.status_code == 429
        body = res_blocked.json()
        assert body["success"] is False
        assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Retry-After" in res_blocked.headers
    finally:
        app_settings.RATE_LIMIT_PER_MINUTE = original_limit
