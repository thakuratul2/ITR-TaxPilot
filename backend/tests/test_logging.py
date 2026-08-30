"""Tests for structured JSON logging and PII masking filter."""

import json
import logging

from app.core.logging import JSONLogFormatter, PIIMaskingFilter, mask_pii


def test_mask_pii_function():
    """Test mask_pii properly redacts PAN and Aadhaar numbers."""
    text_with_pan = "Processing tax return for PAN ABCDE1234F."
    masked_pan = mask_pii(text_with_pan)
    assert "ABCDE1234F" not in masked_pan
    assert "[REDACTED_PAN]" in masked_pan

    text_with_aadhaar = "Aadhaar number is 1234 5678 9012."
    masked_aadhaar = mask_pii(text_with_aadhaar)
    assert "1234 5678 9012" not in masked_aadhaar
    assert "[REDACTED_AADHAAR]" in masked_aadhaar


def test_pii_masking_filter():
    """Test PIIMaskingFilter redacts log records."""
    pii_filter = PIIMaskingFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Taxpayer PAN is ABCDE1234F",
        args=(),
        exc_info=None,
    )
    pii_filter.filter(record)
    assert "ABCDE1234F" not in record.msg
    assert "[REDACTED_PAN]" in record.msg


def test_json_log_formatter():
    """Test JSONLogFormatter produces valid parseable JSON."""
    formatter = JSONLogFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Sample log message",
        args=(),
        exc_info=None,
    )
    record.request_id = "req_12345"

    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_logger"
    assert parsed["message"] == "Sample log message"
    assert parsed["request_id"] == "req_12345"
    assert "timestamp" in parsed
