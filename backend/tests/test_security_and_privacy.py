"""Security, Privacy and Data Protection test suite for Milestone 14."""

import io
import logging
import os
import tempfile
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.logging import PIIMaskingFilter, mask_pii
from app.core.security import (
    mask_aadhaar,
    mask_email,
    mask_pan,
    sanitize_filename,
)
from app.documents.security_checker import inspect_pdf_security
from app.documents.storage import EphemeralStorageManager
from app.main import create_app


@pytest.fixture
def client():
    """Create test client with security headers and middleware active."""
    test_settings = Settings(
        APP_ENV="test",
        DEBUG=False,
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_PER_MINUTE=60,
    )
    app = create_app(settings=test_settings)
    with TestClient(app) as test_client:
        yield test_client


def test_pii_masking_function():
    """Verify mask_pii redacts PAN, Aadhaar, Email, and Phone."""
    raw_text = "Taxpayer PAN ABCDE1234F Aadhaar 1234 5678 9012 email user@example.com phone 9876543210"
    masked = mask_pii(raw_text)
    assert "ABCDE1234F" not in masked
    assert "[REDACTED_PAN]" in masked
    assert "1234 5678 9012" not in masked
    assert "[REDACTED_AADHAAR]" in masked
    assert "user@example.com" not in masked
    assert "[REDACTED_EMAIL]" in masked
    assert "9876543210" not in masked
    assert "[REDACTED_PHONE]" in masked


def test_pii_masking_filter():
    """Verify logging.Filter redacts PII from records and arguments."""
    filter_instance = PIIMaskingFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Processing PAN ABCDE1234F for user@domain.com",
        args=(),
        exc_info=None,
    )

    filter_instance.filter(record)
    assert "ABCDE1234F" not in record.msg
    assert "[REDACTED_PAN]" in record.msg
    assert "[REDACTED_EMAIL]" in record.msg


def test_security_pan_masking_styles():
    """Verify mask_pan supports middle and prefix styles."""
    pan = "ABCDE1234F"
    assert mask_pan(pan, style="middle") == "ABCDE****F"
    assert mask_pan(pan, style="prefix") == "XXXXX1234F"
    assert mask_pan("") == "XXXXX1234X"
    assert mask_pan(None) == "XXXXX1234X"


def test_security_aadhaar_and_email_masking():
    """Verify mask_aadhaar and mask_email format correctly."""
    assert mask_aadhaar("123456789012") == "XXXX-XXXX-9012"
    assert mask_aadhaar("1234 5678 9012") == "XXXX-XXXX-9012"
    assert mask_aadhaar("") == "XXXX-XXXX-XXXX"

    assert mask_email("john.doe@example.com") == "j******e@example.com"
    assert mask_email("ab@test.com") == "a*@test.com"
    assert mask_email("invalid-email") == "u***r@domain.com"


def test_security_response_headers(client):
    """Verify all critical security headers are returned on HTTP responses."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers

    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-XSS-Protection"] == "1; mode=block"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert "camera=()" in headers["Permissions-Policy"]
    assert "max-age=" in headers["Strict-Transport-Security"]


def test_filename_sanitization():
    """Verify path traversal characters and dangerous characters are sanitized."""
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename("..\\..\\windows\\system32\\calc.exe.pdf") == "calc.exe.pdf"
    assert sanitize_filename("safe_report-2024.pdf") == "safe_report-2024.pdf"


def test_pdf_security_magic_bytes():
    """Verify inspect_pdf_security rejects files lacking %PDF- header."""
    res = inspect_pdf_security(b"NOT_A_PDF_FILE")
    assert not res.is_safe
    assert "signature" in res.reason.lower() or "header" in res.reason.lower()


def test_pdf_security_dangerous_js_tokens():
    """Verify inspect_pdf_security detects embedded javascript and launch payloads."""
    malicious_pdf = b"%PDF-1.4\n1 0 obj\n<< /JavaScript (app.alert(1)) >>\nendobj"
    res = inspect_pdf_security(malicious_pdf)
    assert not res.is_safe
    assert "unsafe PDF object" in res.reason

    malicious_launch = b"%PDF-1.4\n1 0 obj\n<< /Launch /F (calc.exe) >>\nendobj"
    res_launch = inspect_pdf_security(malicious_launch)
    assert not res_launch.is_safe


def test_ephemeral_storage_retention():
    """Verify ephemeral storage manager deletes expired files based on retention policy."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = EphemeralStorageManager(base_dir=tmpdir)
        doc1_path = manager.save_ephemeral_file("doc1", "test1.pdf", b"%PDF-1.4 test")
        doc2_path = manager.save_ephemeral_file("doc2", "test2.pdf", b"%PDF-1.4 test")

        assert os.path.exists(doc1_path)
        assert os.path.exists(doc2_path)

        # Explicitly set doc1 modification time to 2 hours ago
        two_hours_ago = time.time() - 7200
        os.utime(os.path.dirname(doc1_path), (two_hours_ago, two_hours_ago))

        # Run cleanup with 30 min retention
        cleaned = manager.cleanup_expired_files(retention_minutes=30)
        assert cleaned >= 1
        assert not os.path.exists(doc1_path)
        assert os.path.exists(doc2_path)


def test_rate_limiter_exceeded():
    """Verify rate limiter triggers 429 when client limit is exceeded."""
    import uuid
    unique_ip = f"172.16.50.{uuid.uuid4().hex[:6]}"
    test_headers = {"X-Forwarded-For": unique_ip}

    test_settings = Settings(
        APP_ENV="test",
        DEBUG=False,
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_PER_MINUTE=3,
    )
    app = create_app(settings=test_settings)
    with TestClient(app) as local_client:
        # 3 requests allowed under /api/v1/health
        r1 = local_client.get("/api/v1/health", headers=test_headers)
        r2 = local_client.get("/api/v1/health", headers=test_headers)
        r3 = local_client.get("/api/v1/health", headers=test_headers)
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r3.status_code == 200

        # 4th request should exceed limit
        r4 = local_client.get("/api/v1/health", headers=test_headers)
        assert r4.status_code == 429
        data = r4.json()
        assert not data["success"]
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Retry-After" in r4.headers
