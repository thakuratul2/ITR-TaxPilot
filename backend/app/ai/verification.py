"""Dual-model cross-verification mechanism for critical tax figures."""


from app.ai.schemas import ExtractedForm16Data
from app.core.logging import get_logger

logger = get_logger("app.ai.verification")

# Threshold for flagging numerical disagreement (in INR)
DISAGREEMENT_TOLERANCE_INR = 10.0


def cross_verify_extractions(
    primary: ExtractedForm16Data,
    secondary: ExtractedForm16Data,
) -> tuple[ExtractedForm16Data, list[str]]:
    """Compare primary extraction against secondary model extraction and annotate disagreements."""
    disagreements: list[str] = []

    # 1. Compare Total Gross Salary
    diff_gross = abs(primary.salary.total_gross_salary - secondary.salary.total_gross_salary)
    if diff_gross > DISAGREEMENT_TOLERANCE_INR:
        disagreements.append(
            f"Total Gross Salary disagreement: Primary={primary.salary.total_gross_salary} vs Secondary={secondary.salary.total_gross_salary}"
        )

    # 2. Compare Standard Deduction
    p_std = primary.salary.standard_deduction_sec_16_ia or 0.0
    s_std = secondary.salary.standard_deduction_sec_16_ia or 0.0
    if abs(p_std - s_std) > DISAGREEMENT_TOLERANCE_INR:
        disagreements.append(f"Standard Deduction disagreement: Primary={p_std} vs Secondary={s_std}")

    # 3. Compare Section 80C
    p_80c = primary.deductions.section_80c or 0.0
    s_80c = secondary.deductions.section_80c or 0.0
    if abs(p_80c - s_80c) > DISAGREEMENT_TOLERANCE_INR:
        disagreements.append(f"Section 80C disagreement: Primary={p_80c} vs Secondary={s_80c}")

    # 4. Compare Total Taxable Income
    diff_taxable = abs(primary.tax.total_taxable_income - secondary.tax.total_taxable_income)
    if diff_taxable > DISAGREEMENT_TOLERANCE_INR:
        disagreements.append(
            f"Total Taxable Income disagreement: Primary={primary.tax.total_taxable_income} vs Secondary={secondary.tax.total_taxable_income}"
        )

    # 5. Compare Total TDS Deducted
    diff_tds = abs(primary.tax.total_tds_deducted - secondary.tax.total_tds_deducted)
    if diff_tds > DISAGREEMENT_TOLERANCE_INR:
        disagreements.append(
            f"Total TDS Deducted disagreement: Primary={primary.tax.total_tds_deducted} vs Secondary={secondary.tax.total_tds_deducted}"
        )

    # Update verification status on primary
    primary.has_dual_verification = True
    primary.disagreements = disagreements

    if disagreements:
        logger.warning(
            "Dual-model verification detected %d disagreement(s): %s",
            len(disagreements),
            disagreements,
        )
        # Adjust overall confidence score downwards if disagreements exist
        if "overall" in primary.confidence_scores:
            primary.confidence_scores["overall"] = max(0.0, primary.confidence_scores["overall"] - 0.15)
    else:
        logger.info("Dual-model verification completed with 100% agreement across all key fields.")
        if "overall" in primary.confidence_scores:
            primary.confidence_scores["overall"] = min(1.0, primary.confidence_scores["overall"] + 0.05)

    return primary, disagreements
