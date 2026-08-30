"""Structured JSON logging with automated PII masking and redaction."""

import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import Any

# Regex patterns for sensitive PII
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", re.IGNORECASE)
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def mask_pii(text: str) -> str:
    """Mask sensitive identifiers from log strings."""
    if not isinstance(text, str):
        return text
    text = PAN_PATTERN.sub("[REDACTED_PAN]", text)
    text = AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", text)
    return text


class PIIMaskingFilter(logging.Filter):
    """Logging filter that redacts PII from log messages and attributes."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = mask_pii(record.msg)

        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: (mask_pii(v) if isinstance(v, str) else v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(mask_pii(arg) if isinstance(arg, str) else arg for arg in record.args)
        return True


class JSONLogFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include request_id / correlation context if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include any extra custom metadata
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            for k, v in record.extra_data.items():
                if k not in log_entry:
                    log_entry[k] = mask_pii(v) if isinstance(v, str) else v

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO", log_format: str = "json", enable_pii_masking: bool = True) -> None:
    """Configure root and application loggers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if log_format.lower() == "json":
        handler.setFormatter(JSONLogFormatter())
    else:
        standard_format = "%(asctime)s [%(levelname)s] %(name)s (%(request_id)s): %(message)s"
        handler.setFormatter(logging.Formatter(standard_format))

    if enable_pii_masking:
        handler.addFilter(PIIMaskingFilter())

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get named logger instance."""
    return logging.getLogger(name)
