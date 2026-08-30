"""Validation utilities for uploaded document files."""

from app.core.config import get_settings
from app.core.exceptions import FileSizeExceededError, InvalidFileFormatError


def validate_pdf_file(
    content_type: str | None,
    filename: str | None,
    file_bytes: bytes,
) -> None:
    """Validate uploaded file MIME type, extension, and size limits."""
    settings = get_settings()

    # 1. Content-Type and Extension check
    allowed_mimes = settings.allowed_mimes
    is_valid_mime = content_type in allowed_mimes if content_type else False
    is_valid_ext = filename.lower().endswith(".pdf") if filename else False

    if not (is_valid_mime or is_valid_ext):
        raise InvalidFileFormatError(content_type or "unknown", allowed_mimes)

    # 2. Non-empty check
    if not file_bytes or len(file_bytes) == 0:
        raise InvalidFileFormatError("empty_file", allowed_mimes)

    # 3. File size check
    file_size_mb = len(file_bytes) / (1024 * 1024)
    if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise FileSizeExceededError(file_size_mb, settings.MAX_UPLOAD_SIZE_MB)
