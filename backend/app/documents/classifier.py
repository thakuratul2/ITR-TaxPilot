"""Document classifier detecting Form 16 Part A and Part B patterns."""

import re

from app.documents.models import DocumentClassification

# Core Form 16 markers
FORM_16_PRIMARY_MARKERS = [
    "FORM NO. 16",
    "FORM 16",
    "Certificate under section 203",
    "Income-tax Act, 1961",
]

PART_A_MARKERS = [
    "PART A",
    "Name and address of the Employer",
    "Name and address of the Deductor",
    "TAN of the Deductor",
    "Summary of amount paid",
    "Quarter",
]

PART_B_MARKERS = [
    "PART B",
    "Gross Salary",
    "Salary as per provisions contained in sec. 17(1)",
    "Standard Deduction u/s 16(ia)",
    "Deductions under Chapter VI-A",
    "Section 80C",
    "Tax on total income",
    "Rebate under section 87A",
]

AY_REGEX = re.compile(r"Assessment\s*Year\s*[:\-]?\s*(202[0-9]\s*[-–/]\s*[0-9]{2,4})", re.IGNORECASE)


def classify_form16_document(full_text: str) -> DocumentClassification:
    """Classify extracted text to verify Form 16 structure and detect Part A/B sections."""
    detected_markers: list[str] = []
    text_upper = full_text.upper()

    # Check primary Form 16 markers
    primary_count = 0
    for marker in FORM_16_PRIMARY_MARKERS:
        if marker.upper() in text_upper:
            detected_markers.append(marker)
            primary_count += 1

    # Check Part A markers
    part_a_count = 0
    for marker in PART_A_MARKERS:
        if marker.upper() in text_upper:
            detected_markers.append(marker)
            part_a_count += 1
    has_part_a = part_a_count >= 2

    # Check Part B markers
    part_b_count = 0
    for marker in PART_B_MARKERS:
        if marker.upper() in text_upper:
            detected_markers.append(marker)
            part_b_count += 1
    has_part_b = part_b_count >= 2

    # Assessment Year detection
    detected_ay = None
    ay_match = AY_REGEX.search(full_text)
    if ay_match:
        raw_ay = ay_match.group(1).replace(" ", "").replace("–", "-").replace("/", "-")
        # Normalize format to YYYY-YY (e.g. 2026-27)
        if len(raw_ay) == 9 and raw_ay[4] == "-":
            detected_ay = f"{raw_ay[:5]}{raw_ay[7:]}"
        else:
            detected_ay = raw_ay

    # Confidence calculation
    total_signals = primary_count * 2 + part_a_count + part_b_count
    is_form16 = (primary_count >= 1 or (has_part_a and has_part_b)) and len(full_text.strip()) > 50

    confidence = min(1.0, round(total_signals / 10.0, 2)) if is_form16 else 0.0

    return DocumentClassification(
        is_form16=is_form16,
        has_part_a=has_part_a,
        has_part_b=has_part_b,
        detected_ay=detected_ay,
        confidence=confidence,
        detected_markers=detected_markers,
    )
