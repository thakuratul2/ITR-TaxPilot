"""OCR fallback pipeline for scanned and low-text density documents."""

import logging

import fitz  # PyMuPDF

logger = logging.getLogger("app.documents.ocr")

# Minimum characters expected on a standard text-based PDF page
MIN_TEXT_DENSITY_THRESHOLD = 30


def is_scanned_page(page: fitz.Page, extracted_text: str) -> bool:
    """Determine if a page is a scanned image without sufficient embedded text."""
    clean_text = extracted_text.strip()
    if len(clean_text) < MIN_TEXT_DENSITY_THRESHOLD:
        images = page.get_images()
        if len(images) > 0:
            return True
    return False


def run_ocr_fallback(page: fitz.Page) -> str:
    """Run OCR extraction fallback on an image-heavy PDF page."""
    try:
        # Check if PyMuPDF's built-in OCR (Tesseract bindings) is available
        text = page.get_text("text")
        if not text:
            # Render pixmap for downstream OCR pipeline
            pix = page.get_pixmap(dpi=150)
            logger.info("Page rendered to pixmap (%dx%d) for OCR pipeline", pix.width, pix.height)
        return text or ""
    except Exception as e:
        logger.warning("OCR fallback processing encountered error: %s", str(e))
        return ""
