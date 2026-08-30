"""Security and data sanitization utilities."""

import secrets
import string


def generate_request_id() -> str:
    """Generate a secure unique correlation request ID."""
    return f"req_{secrets.token_hex(8)}"


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded document filenames to prevent directory traversal."""
    allowed_chars = string.ascii_letters + string.digits + "._-"
    sanitized = "".join(c for c in filename if c in allowed_chars)
    return sanitized or f"document_{secrets.token_hex(4)}.pdf"
