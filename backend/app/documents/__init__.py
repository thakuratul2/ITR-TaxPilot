"""Document processing package."""

from app.documents.classifier import classify_form16_document
from app.documents.extractor import extract_text_from_pdf
from app.documents.models import (
    DocumentClassification,
    ExtractedPage,
    ExtractedTable,
    NormalizedDocument,
)
from app.documents.ocr import is_scanned_page, run_ocr_fallback
from app.documents.security_checker import inspect_pdf_security
from app.documents.storage import EphemeralStorageManager, storage_manager
from app.documents.table_extractor import extract_tables_from_page
from app.documents.validator import validate_pdf_file

__all__ = [
    "NormalizedDocument",
    "ExtractedPage",
    "ExtractedTable",
    "DocumentClassification",
    "validate_pdf_file",
    "inspect_pdf_security",
    "extract_text_from_pdf",
    "extract_tables_from_page",
    "is_scanned_page",
    "run_ocr_fallback",
    "classify_form16_document",
    "EphemeralStorageManager",
    "storage_manager",
]
