"""Custom application exceptions with domain error codes."""

from typing import Any


class AppException(Exception):
    """Base application exception with standardized code and HTTP status code."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class DocumentNotFoundError(AppException):
    """Raised when a requested document ID does not exist."""

    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document with ID '{document_id}' was not found.",
            code="DOCUMENT_NOT_FOUND",
            status_code=404,
            details={"document_id": document_id},
        )


class JobNotFoundError(AppException):
    """Raised when a requested job ID does not exist."""

    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job with ID '{job_id}' was not found.",
            code="JOB_NOT_FOUND",
            status_code=404,
            details={"job_id": job_id},
        )


class AnalysisNotFoundError(AppException):
    """Raised when a requested analysis ID does not exist."""

    def __init__(self, analysis_id: str):
        super().__init__(
            message=f"Analysis with ID '{analysis_id}' was not found.",
            code="ANALYSIS_NOT_FOUND",
            status_code=404,
            details={"analysis_id": analysis_id},
        )


class InvalidFileFormatError(AppException):
    """Raised when an uploaded file is not a supported format."""

    def __init__(self, content_type: str, allowed: list[str]):
        super().__init__(
            message=f"Unsupported file type '{content_type}'. Allowed types: {', '.join(allowed)}.",
            code="INVALID_FILE_FORMAT",
            status_code=415,
            details={"content_type": content_type, "allowed": allowed},
        )


class FileSizeExceededError(AppException):
    """Raised when an uploaded file exceeds the allowed size limit."""

    def __init__(self, file_size_mb: float, max_mb: int):
        super().__init__(
            message=f"File size ({file_size_mb:.2f} MB) exceeds maximum limit of {max_mb} MB.",
            code="FILE_SIZE_EXCEEDED",
            status_code=413,
            details={"file_size_mb": file_size_mb, "max_mb": max_mb},
        )


class TaxRuleNotFoundError(AppException):
    """Raised when rules for a specified Assessment Year are not available."""

    def __init__(self, assessment_year: str):
        super().__init__(
            message=f"Tax rules for Assessment Year '{assessment_year}' are not configured.",
            code="TAX_RULE_NOT_FOUND",
            status_code=422,
            details={"assessment_year": assessment_year},
        )


class AIProviderError(AppException):
    """Raised when an external AI provider fails."""

    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"AI provider '{provider}' failed to process the request.",
            code="AI_PROVIDER_ERROR",
            status_code=502,
            details={"provider": provider, "reason": reason},
        )
