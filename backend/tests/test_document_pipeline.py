"""Comprehensive tests for Milestone 3 Form 16 Document Pipeline."""

import io

import fitz  # PyMuPDF
from fastapi.testclient import TestClient

from app.documents.classifier import classify_form16_document
from app.documents.extractor import extract_text_from_pdf
from app.documents.security_checker import inspect_pdf_security
from app.documents.storage import EphemeralStorageManager
from app.services.document_service import DocumentService


def create_sample_form16_pdf() -> bytes:
    """Generate a valid in-memory Form 16 PDF fixture using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()

    # Add standard Form 16 headers and content
    text = (
        "FORM NO. 16\n"
        "Certificate under section 203 of the Income-tax Act, 1961\n"
        "Assessment Year: 2026-27\n"
        "Financial Year: 2025-26\n"
        "PART A\n"
        "Name and address of the Employer: Acme Corp\n"
        "TAN of the Deductor: DELA12345B\n"
        "Summary of amount paid and tax deducted\n\n"
        "PART B\n"
        "Gross Salary: 1200000\n"
        "Standard Deduction u/s 16(ia): 75000\n"
        "Deductions under Chapter VI-A\n"
        "Section 80C: 150000\n"
        "Tax on total income: 67600\n"
    )
    page.insert_text((50, 50), text, fontsize=11)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_inspect_pdf_security_valid():
    """Test security inspection passes for normal PDF."""
    pdf_bytes = create_sample_form16_pdf()
    result = inspect_pdf_security(pdf_bytes)
    assert result.is_safe is True


def test_inspect_pdf_security_malicious_js():
    """Test security inspection rejects PDF with embedded JavaScript token."""
    malicious_bytes = b"%PDF-1.4\n1 0 obj\n<< /JS (app.alert('pwned')) /JavaScript >>\nendobj\n%%EOF"
    result = inspect_pdf_security(malicious_bytes)
    assert result.is_safe is False
    assert "unsafe PDF object" in result.reason


def test_inspect_pdf_security_invalid_header():
    """Test security inspection rejects non-PDF file."""
    invalid_bytes = b"Hello World not a pdf"
    result = inspect_pdf_security(invalid_bytes)
    assert result.is_safe is False
    assert "Missing '%PDF-'" in result.reason


def test_pdf_text_extraction():
    """Test PyMuPDF extracts text correctly."""
    pdf_bytes = create_sample_form16_pdf()
    pages = extract_text_from_pdf(pdf_bytes)
    assert len(pages) == 1
    assert "FORM NO. 16" in pages[0].text
    assert "Assessment Year: 2026-27" in pages[0].text


def test_form16_classifier():
    """Test classifier detects Form 16, Part A, Part B, and Assessment Year."""
    sample_text = (
        "FORM NO. 16 Certificate under section 203 "
        "Assessment Year: 2026-27 "
        "PART A Name and address of the Deductor TAN of the Deductor "
        "PART B Gross Salary Standard Deduction u/s 16(ia) Deductions under Chapter VI-A"
    )
    classification = classify_form16_document(sample_text)
    assert classification.is_form16 is True
    assert classification.has_part_a is True
    assert classification.has_part_b is True
    assert classification.detected_ay == "2026-27"
    assert classification.confidence >= 0.7


def test_ephemeral_storage(tmp_path):
    """Test ephemeral storage lifecycle: saving and deleting files."""
    storage = EphemeralStorageManager(base_dir=tmp_path)
    file_path = storage.save_ephemeral_file("test-doc-1", "form16.pdf", b"test pdf content")
    assert file_path is not None
    assert tmp_path.joinpath("test-doc-1", "form16.pdf").exists()

    deleted = storage.delete_document_files("test-doc-1")
    assert deleted is True
    assert not tmp_path.joinpath("test-doc-1").exists()


def test_document_service_pipeline():
    """Test DocumentService orchestrates full pipeline end-to-end."""
    pdf_bytes = create_sample_form16_pdf()
    normalized_doc, path = DocumentService.process_form16_upload(
        filename="my_form16.pdf",
        content_type="application/pdf",
        file_bytes=pdf_bytes,
    )
    assert normalized_doc.total_pages == 1
    assert normalized_doc.classification.is_form16 is True
    assert normalized_doc.classification.detected_ay == "2026-27"
    assert "Gross Salary" in normalized_doc.full_text


def test_api_upload_form16_endpoint(client: TestClient):
    """Test uploading generated PDF to POST /api/v1/documents/form16."""
    pdf_bytes = create_sample_form16_pdf()
    files = {"file": ("taxpayer_form16.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    response = client.post("/api/v1/documents/form16", files=files)
    assert response.status_code == 202

    payload = response.json()
    assert payload["success"] is True
    assert "2026-27" in payload["data"]["message"] or "processed" in payload["data"]["message"]
