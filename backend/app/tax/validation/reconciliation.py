"""Part A vs Part B TDS reconciliation and duplicate field resolution."""


from app.ai.schemas import ExtractedForm16Data
from app.tax.validation.models import ValidationIssue, ValidationSeverity

TDS_TOLERANCE_INR = 5.0


def reconcile_part_a_and_part_b(
    extracted: ExtractedForm16Data,
    part_a_tds_total: float | None = None,
) -> list[ValidationIssue]:
    """Verify that TDS deducted in Part A matches tax deducted in Part B."""
    issues: list[ValidationIssue] = []

    if part_a_tds_total is not None:
        part_b_tds = extracted.tax.total_tds_deducted
        diff = abs(part_a_tds_total - part_b_tds)

        if diff > TDS_TOLERANCE_INR:
            issues.append(
                ValidationIssue(
                    field="total_tds_deducted",
                    rule_code="TDS_PART_A_PART_B_MISMATCH",
                    message=(
                        f"TDS mismatch between Part A (₹{part_a_tds_total:,.2f}) "
                        f"and Part B (₹{part_b_tds:,.2f}). Difference of ₹{diff:,.2f}."
                    ),
                    severity=ValidationSeverity.WARNING,
                    actual_value=part_b_tds,
                    expected_value=part_a_tds_total,
                )
            )

    return issues


def resolve_duplicate_breakdown_items(
    items: dict[str, float],
) -> tuple[dict[str, float], list[ValidationIssue]]:
    """Normalize and aggregate duplicate allowance/deduction items with varying casing/whitespace."""
    normalized_dict: dict[str, float] = {}
    issues: list[ValidationIssue] = []

    for key, value in items.items():
        clean_key = " ".join(key.strip().upper().split())
        if clean_key in normalized_dict:
            # Aggregate and record duplicate resolution
            old_val = normalized_dict[clean_key]
            normalized_dict[clean_key] = old_val + value
            issues.append(
                ValidationIssue(
                    field=key,
                    rule_code="DUPLICATE_ITEM_RESOLVED",
                    message=f"Duplicate entry for '{clean_key}' consolidated (₹{old_val} + ₹{value}).",
                    severity=ValidationSeverity.INFO,
                    actual_value=value,
                    expected_value=normalized_dict[clean_key],
                )
            )
        else:
            normalized_dict[clean_key] = value

    return normalized_dict, issues
