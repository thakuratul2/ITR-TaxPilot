"""Confidence evaluation and human review flagging."""


from app.ai.schemas import ExtractedForm16Data
from app.tax.validation.models import ValidationIssue, ValidationSeverity

LOW_CONFIDENCE_THRESHOLD = 0.85


def evaluate_confidence_and_review_requirements(
    extracted: ExtractedForm16Data,
    issues: list[ValidationIssue],
) -> tuple[bool, list[str]]:
    """Determine if document data requires manual taxpayer confirmation before tax engine filing."""
    review_reasons: list[str] = []

    # 1. Check field level confidence scores
    for field_name, score in extracted.confidence_scores.items():
        if field_name != "overall" and score < LOW_CONFIDENCE_THRESHOLD:
            review_reasons.append(
                f"Field '{field_name}' has lower extraction confidence ({score:.0%}). Please verify."
            )

    # 2. Check for validation warning issues
    warning_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING)
    if warning_count > 0:
        review_reasons.append(f"{warning_count} arithmetic/reconciliation warning(s) detected.")

    # 3. Check for dual-model discrepancies
    if extracted.disagreements:
        review_reasons.append(f"AI models disagreed on {len(extracted.disagreements)} field(s).")

    requires_review = len(review_reasons) > 0
    return requires_review, review_reasons
