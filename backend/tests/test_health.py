"""Tests for the /health and /api/v1/health endpoints."""

from fastapi.testclient import TestClient


def test_root_health_endpoint(client: TestClient):
    """Test GET /health returns 200 and standard envelope structure."""
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert payload["request_id"] is not None
    assert "data" in payload

    data = payload["data"]
    assert data["status"] == "healthy"
    assert data["app_name"] == "ITR-TaxPilot-Test"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "test"
    assert "timestamp" in data


def test_api_v1_health_endpoint(client: TestClient):
    """Test GET /api/v1/health returns 200 and standard envelope structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert payload["data"]["status"] == "healthy"


def test_request_id_header(client: TestClient):
    """Test that X-Request-ID and X-Process-Time-MS response headers are returned."""
    custom_req_id = "test-custom-req-id-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_req_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_req_id
    assert "X-Process-Time-MS" in response.headers


def test_404_error_envelope(client: TestClient):
    """Test that unhandled routes return standard error envelope."""
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404

    payload = response.json()
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["error"]["code"] == "HTTP_404"
