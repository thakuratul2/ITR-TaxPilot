"""PDF text extraction using PyMuPDF (fitz)."""

import fitz  # PyMuPDF

from app.documents.models import ExtractedPage


def extract_text_from_pdf(pdf_bytes: bytes) -> list[ExtractedPage]:
    """Extract structured text and page content from raw PDF bytes using PyMuPDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[ExtractedPage] = []

    try:
        for idx, page in enumerate(doc, start=1):
            page_text = page.get_text("text").strip()
            pages.append(
                ExtractedPage(
                    page_number=idx,
                    text=page_text,
                    tables=[],
                    is_ocr=False,
                )
            )
    finally:
        doc.close()

    return pages
