"""Pydantic schemas package."""

from app.schemas.analysis import AnalysisData, TaxCalculationSummary
from app.schemas.base import APIError, APIResponse
from app.schemas.document import DocumentResponse, DocumentUploadPayload
from app.schemas.health import HealthData, HealthResponse
from app.schemas.job import JobData

__all__ = [
    "APIResponse",
    "APIError",
    "HealthResponse",
    "HealthData",
    "DocumentResponse",
    "DocumentUploadPayload",
    "JobData",
    "AnalysisData",
    "TaxCalculationSummary",
]
