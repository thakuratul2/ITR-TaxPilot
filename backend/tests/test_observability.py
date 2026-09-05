"""Test suite for Milestone 16: Observability, Metrics, Health Inspection, and Log Sanitization."""

import json
import logging
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.logging import JSONLogFormatter, PIIMaskingFilter
from app.core.telemetry import metrics_collector


def test_structured_json_logging_format():
    """Verify JSONLogFormatter produces valid JSON log records with standard keys."""
    formatter = JSONLogFormatter()
    record = logging.LogRecord(
        name="test_observability",
        level=logging.INFO,
        pathname="telemetry.py",
        lineno=42,
        msg="Processing transaction completed successfully",
        args=(),
        exc_info=None,
    )
    record.request_id = "req_obs_test_123"

    formatted_str = formatter.format(record)
    log_dict = json.loads(formatted_str)

    assert "timestamp" in log_dict
    assert log_dict["level"] == "INFO"
    assert log_dict["logger"] == "test_observability"
    assert log_dict["message"] == "Processing transaction completed successfully"
    assert log_dict["request_id"] == "req_obs_test_123"
    assert log_dict["line"] == 42


def test_telemetry_metrics_collection():
    """Verify MetricsCollector accurately tracks request rates, latencies, and business counters."""
    metrics_collector.reset()

    # Record simulated requests
    metrics_collector.record_request("GET", "/api/v1/health", 200, 10.5)
    metrics_collector.record_request("GET", "/api/v1/health", 200, 15.5)
    metrics_collector.record_request("POST", "/api/v1/documents/form16", 400, 25.0)

    # Increment business operation counters
    metrics_collector.increment_document_processed()
    metrics_collector.increment_document_processed()
    metrics_collector.increment_tax_calculation()
    metrics_collector.record_error("INVALID_FILE_FORMAT")

    summary = metrics_collector.get_metrics_summary()

    assert summary["total_requests"] == 3
    assert summary["total_errors"] == 1
    assert summary["documents_processed"] == 2
    assert summary["tax_calculations_performed"] == 1
    assert summary["error_breakdown"]["INVALID_FILE_FORMAT"] == 1

    get_health_stats = summary["endpoints"]["GET /api/v1/health"]
    assert get_health_stats["requests"] == 2
    assert get_health_stats["errors"] == 0
    assert get_health_stats["avg_latency_ms"] == 13.0


def test_metrics_api_endpoint(client: TestClient):
    """Verify GET /api/v1/metrics endpoint returns operational metrics."""
    unique_ip = f"10.150.1.{uuid.uuid4().hex[:4]}"
    # Generate some traffic
    client.get("/api/v1/health", headers={"X-Forwarded-For": unique_ip})

    response = client.get("/api/v1/metrics", headers={"X-Forwarded-For": unique_ip})
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "uptime_seconds" in data
    assert "total_requests" in data
    assert "endpoints" in data


def test_comprehensive_health_probes(client: TestClient):
    """Verify health check endpoint reports status for DB, Redis, Storage, and AI providers."""
    unique_ip = f"10.150.1.{uuid.uuid4().hex[:4]}"
    response = client.get("/health", headers={"X-Forwarded-For": unique_ip})
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["status"] == "healthy"
    assert "database" in data
    assert "redis" in data
    assert "storage" in data
    assert data["storage"] == "ready"
    assert "ai_providers" in data
    assert isinstance(data["ai_providers"], dict)
    assert "gemini" in data["ai_providers"]


def test_log_sanitization_audit_prevents_pii_leakage():
    """Verify PII Filter scrubs PAN, Aadhaar, and Emails from exception traces and messages."""
    pii_filter = PIIMaskingFilter()
    msg = "User error with PAN ABCDE1234F, Aadhaar 9999 8888 7777, and email admin@secret.com"
    record = logging.LogRecord(
        name="test_audit",
        level=logging.ERROR,
        pathname="audit.py",
        lineno=100,
        msg=msg,
        args=(),
        exc_info=None,
    )

    pii_filter.filter(record)
    assert "ABCDE1234F" not in record.msg
    assert "9999 8888 7777" not in record.msg
    assert "admin@secret.com" not in record.msg
    assert "[REDACTED_PAN]" in record.msg
    assert "[REDACTED_AADHAAR]" in record.msg
    assert "[REDACTED_EMAIL]" in record.msg
