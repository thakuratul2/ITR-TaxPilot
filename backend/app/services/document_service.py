"""Document processing service pipeline."""

import hashlib
import uuid

import fitz  # PyMuPDF

from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.core.security import sanitize_filename
from app.documents.classifier import classify_form16_document
from app.documents.models import NormalizedDocument
from app.documents.ocr import is_scanned_page, run_ocr_fallback
from app.documents.security_checker import inspect_pdf_security
from app.documents.storage import storage_manager
from app.documents.table_extractor import extract_tables_from_page
from app.documents.validator import validate_pdf_file

logger = get_logger("app.services.document_service")


class DocumentService:
    """End-to-end pipeline service for Form 16 document validation, extraction, and normalization."""

    @staticmethod
    def process_form16_upload(
        filename: str,
        content_type: str,
        file_bytes: bytes,
    ) -> tuple[NormalizedDocument, str]:
        """Execute full upload pipeline: validate -> security scan -> extract -> classify -> normalize."""
        # 1. Validation checks
        validate_pdf_file(content_type, filename, file_bytes)

        # 2. Malicious payload inspection
        security_result = inspect_pdf_security(file_bytes)
        if not security_result.is_safe:
            raise AppException(
                message=security_result.reason,
                code="SECURITY_CHECK_FAILED",
                status_code=400,
            )

        # 3. Ephemeral storage and SHA256 computation
        document_id = str(uuid.uuid4())
        sanitized_name = sanitize_filename(filename)
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        storage_path = storage_manager.save_ephemeral_file(document_id, sanitized_name, file_bytes)
        logger.info("Processing document %s (SHA256: %s)", document_id, sha256_hash[:12])

        # 4. PyMuPDF text & table extraction
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        all_text_fragments = []

        try:
            for idx, page in enumerate(doc, start=1):
                page_text = page.get_text("text").strip()
                is_ocr = False

                # 5. Check if page is scanned and needs OCR fallback
                if is_scanned_page(page, page_text):
                    ocr_text = run_ocr_fallback(page)
                    if ocr_text:
                        page_text = ocr_text.strip()
                        is_ocr = True

                # Extract tabular structures from the page
                tables = extract_tables_from_page(page, idx)

                all_text_fragments.append(page_text)
                from app.documents.models import ExtractedPage
                pages.append(
                    ExtractedPage(
                        page_number=idx,
                        text=page_text,
                        tables=tables,
                        is_ocr=is_ocr,
                    )
                )
        finally:
            doc.close()

        full_text = "\n\n".join(all_text_fragments)

        # 6. Document Classification & Assessment Year detection
        classification = classify_form16_document(full_text)

        normalized_doc = NormalizedDocument(
            document_id=document_id,
            filename=sanitized_name,
            file_size_bytes=len(file_bytes),
            total_pages=len(pages),
            pages=pages,
            classification=classification,
            full_text=full_text,
        )

        logger.info(
            "Document %s processed: %d pages, is_form16=%s, detected_ay=%s (confidence=%.2f)",
            document_id,
            len(pages),
            classification.is_form16,
            classification.detected_ay,
            classification.confidence,
        )

        return normalized_doc, storage_path
