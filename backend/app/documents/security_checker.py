"""Security inspection and malware/malicious construct rejection for uploaded PDFs."""

import re

# PDF header signature (%PDF-1.x)
PDF_MAGIC_BYTES = b"%PDF-"

# Dangerous PDF tokens / actions
DANGEROUS_PDF_TOKENS = [
    re.compile(rb"/JavaScript\b", re.IGNORECASE),
    re.compile(rb"/JS\b", re.IGNORECASE),
    re.compile(rb"/Launch\b", re.IGNORECASE),
    re.compile(rb"/EmbeddedFiles\b", re.IGNORECASE),
    re.compile(rb"/SubmitForm\b", re.IGNORECASE),
    re.compile(rb"/ImportData\b", re.IGNORECASE),
]


class SecurityScanResult:
    """Security verification result container."""
    def __init__(self, is_safe: bool, reason: str = ""):
        self.is_safe = is_safe
        self.reason = reason


def inspect_pdf_security(file_bytes: bytes) -> SecurityScanResult:
    """Inspect raw PDF bytes for validity and malicious payload constructs."""
    if not file_bytes:
        return SecurityScanResult(False, "Empty file provided.")

    # 1. Magic bytes validation
    if not file_bytes.startswith(PDF_MAGIC_BYTES):
        return SecurityScanResult(False, "Invalid PDF header: Missing '%PDF-' signature.")

    # 2. Check for dangerous PDF action objects
    for pattern in DANGEROUS_PDF_TOKENS:
        if pattern.search(file_bytes):
            token_name = pattern.pattern.decode("latin1")
            return SecurityScanResult(
                False,
                f"Potentially unsafe PDF object detected: '{token_name}'. Executable scripts are not allowed.",
            )

    return SecurityScanResult(True, "Security checks passed.")
