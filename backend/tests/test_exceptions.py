"""Tests for custom domain exceptions."""

from app.core.exceptions import (
    AIProviderError,
    AnalysisNotFoundError,
    DocumentNotFoundError,
    FileSizeExceededError,
    InvalidFileFormatError,
    JobNotFoundError,
    TaxRuleNotFoundError,
)


def test_custom_exception_codes():
    """Verify error codes and status codes on custom exceptions."""
    doc_err = DocumentNotFoundError("doc-abc")
    assert doc_err.code == "DOCUMENT_NOT_FOUND"
    assert doc_err.status_code == 404
    assert doc_err.details["document_id"] == "doc-abc"

    job_err = JobNotFoundError("job-123")
    assert job_err.code == "JOB_NOT_FOUND"
    assert job_err.status_code == 404

    analysis_err = AnalysisNotFoundError("analysis-999")
    assert analysis_err.code == "ANALYSIS_NOT_FOUND"
    assert analysis_err.status_code == 404

    mime_err = InvalidFileFormatError("image/png", ["application/pdf"])
    assert mime_err.code == "INVALID_FILE_FORMAT"
    assert mime_err.status_code == 415

    size_err = FileSizeExceededError(15.5, 10)
    assert size_err.code == "FILE_SIZE_EXCEEDED"
    assert size_err.status_code == 413

    rule_err = TaxRuleNotFoundError("2030-31")
    assert rule_err.code == "TAX_RULE_NOT_FOUND"
    assert rule_err.status_code == 422

    ai_err = AIProviderError("gemini", "Rate limit exceeded")
    assert ai_err.code == "AI_PROVIDER_ERROR"
    assert ai_err.status_code == 502
