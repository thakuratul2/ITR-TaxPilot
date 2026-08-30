"""Normalized document representation data models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ExtractedTable(BaseModel):
    """Extracted table from a document page."""
    page_number: int = Field(..., description="1-indexed page number")
    headers: list[str] = Field(default_factory=list, description="Table column headers")
    rows: list[list[str]] = Field(default_factory=list, description="Table row cells")


class ExtractedPage(BaseModel):
    """Normalized page representation."""
    page_number: int = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Extracted text on page")
    tables: list[ExtractedTable] = Field(default_factory=list, description="Extracted tables on page")
    is_ocr: bool = Field(default=False, description="True if OCR was utilized for this page")


class DocumentClassification(BaseModel):
    """Classification details for uploaded document."""
    is_form16: bool = Field(..., description="True if document exhibits Form 16 patterns")
    has_part_a: bool = Field(default=False, description="True if Form 16 Part A detected")
    has_part_b: bool = Field(default=False, description="True if Form 16 Part B detected")
    detected_ay: str | None = Field(default=None, description="Detected Assessment Year if found in text")
    confidence: float = Field(default=0.0, description="Classification confidence score 0.0 to 1.0")
    detected_markers: list[str] = Field(default_factory=list, description="Key markers identified")


class NormalizedDocument(BaseModel):
    """Standardized normalized document model for AI extraction and analysis pipeline."""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="Size of file in bytes")
    total_pages: int = Field(..., description="Total pages processed")
    pages: list[ExtractedPage] = Field(default_factory=list, description="Extracted page list")
    classification: DocumentClassification = Field(..., description="Document classification")
    full_text: str = Field(..., description="Aggregated sanitized text across all pages")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Extraction timestamp")
