"""Multi-Employer Form 16 aggregation engine for job switchers."""

from pydantic import BaseModel, Field
from app.tax.rules.base import TaxRegime


class EmployerForm16Input(BaseModel):
    """Extracted Form 16 payload from a single employer."""
    employer_name: str
    employer_tan: str
    period_from: str = ""
    period_to: str = ""
    gross_salary_sec17_1: float = 0.0
    perquisites_sec17_2: float = 0.0
    profits_in_lieu_sec17_3: float = 0.0
    section_10_exemptions: float = 0.0  # HRA, LTA, etc.
    standard_deduction_claimed: float = 0.0
    professional_tax: float = 0.0
    chapter_via_80c: float = 0.0
    chapter_via_80d: float = 0.0
    chapter_via_80ccd_1b: float = 0.0
    chapter_via_other: float = 0.0
    tds_deducted: float = 0.0


class AggregatedSalaryProfile(BaseModel):
    """Consolidated salary and tax profile across all employers in the financial year."""
    number_of_employers: int
    employer_names: list[str]
    total_gross_salary_sec17: float
    total_sec10_exemptions: float
    net_salary_before_deductions: float
    consolidated_standard_deduction: float
    consolidated_professional_tax: float
    consolidated_80c: float
    consolidated_80d: float
    consolidated_80ccd_1b: float
    total_chapter_via_deductions: float
    total_tds_deducted: float
    duplicate_standard_deduction_warning: bool = False
    potential_tax_shortfall_warning: bool = False
    warnings: list[str] = Field(default_factory=list)


class MultiForm16Aggregator:
    """Aggregates multiple Form 16s, deduplicating exemptions and standard deductions."""

    MAX_80C_LIMIT: float = 150000.0
    MAX_80CCD_1B_LIMIT: float = 50000.0
    MAX_80D_LIMIT: float = 100000.0
    MAX_PROFESSIONAL_TAX_LIMIT: float = 2500.0

    @classmethod
    def aggregate(
        cls,
        form16_list: list[EmployerForm16Input],
        regime: TaxRegime = TaxRegime.NEW,
        assessment_year: str = "2025-26",
    ) -> AggregatedSalaryProfile:
        """Consolidate multiple Form 16s into a single compliant salary profile."""
        if not form16_list:
            raise ValueError("At least one Form 16 is required for aggregation.")

        employer_names = [f.employer_name for f in form16_list]
        num_employers = len(form16_list)

        total_gross = sum(
            (f.gross_salary_sec17_1 + f.perquisites_sec17_2 + f.profits_in_lieu_sec17_3)
            for f in form16_list
        )

        total_sec10 = sum(f.section_10_exemptions for f in form16_list)
        total_tds = sum(f.tds_deducted for f in form16_list)

        # Standard deduction limit based on regime and AY
        std_ded_limit = 75000.0 if (regime == TaxRegime.NEW and assessment_year >= "2025-26") else 50000.0

        # Enforce single Standard Deduction
        consolidated_std_ded = min(std_ded_limit, total_gross)

        # Professional tax capped at ₹2,500 total
        raw_pt = sum(f.professional_tax for f in form16_list)
        consolidated_pt = min(raw_pt, cls.MAX_PROFESSIONAL_TAX_LIMIT) if regime == TaxRegime.OLD else 0.0

        # Chapter VI-A Deductions capped at statutory limits
        raw_80c = sum(f.chapter_via_80c for f in form16_list)
        raw_80d = sum(f.chapter_via_80d for f in form16_list)
        raw_80ccd = sum(f.chapter_via_80ccd_1b for f in form16_list)
        raw_other = sum(f.chapter_via_other for f in form16_list)

        consolidated_80c = min(raw_80c, cls.MAX_80C_LIMIT) if regime == TaxRegime.OLD else 0.0
        consolidated_80d = min(raw_80d, cls.MAX_80D_LIMIT) if regime == TaxRegime.OLD else 0.0
        consolidated_80ccd = min(raw_80ccd, cls.MAX_80CCD_1B_LIMIT) if regime == TaxRegime.OLD else 0.0
        consolidated_other = raw_other if regime == TaxRegime.OLD else 0.0

        total_chapter_via = consolidated_80c + consolidated_80d + consolidated_80ccd + consolidated_other

        net_salary = max(0.0, total_gross - (total_sec10 if regime == TaxRegime.OLD else 0.0))

        # Warnings for multi-employer scenarios
        warnings = []
        duplicate_std_ded = False
        potential_shortfall = False

        if num_employers > 1:
            total_claimed_std = sum(f.standard_deduction_claimed for f in form16_list)
            if total_claimed_std > std_ded_limit:
                duplicate_std_ded = True
                warnings.append(
                    f"Multiple employers provided Standard Deduction totaling ₹{total_claimed_std:,.2f}. "
                    f"Consolidated allowable Standard Deduction is capped at ₹{std_ded_limit:,.2f}."
                )

            potential_shortfall = True
            warnings.append(
                "Multiple Form 16s detected. Because each employer applied lower tax slabs independently, "
                "additional tax may be payable upon combining incomes."
            )

        return AggregatedSalaryProfile(
            number_of_employers=num_employers,
            employer_names=employer_names,
            total_gross_salary_sec17=round(total_gross, 2),
            total_sec10_exemptions=round(total_sec10, 2),
            net_salary_before_deductions=round(net_salary, 2),
            consolidated_standard_deduction=round(consolidated_std_ded, 2),
            consolidated_professional_tax=round(consolidated_pt, 2),
            consolidated_80c=round(consolidated_80c, 2),
            consolidated_80d=round(consolidated_80d, 2),
            consolidated_80ccd_1b=round(consolidated_80ccd, 2),
            total_chapter_via_deductions=round(total_chapter_via, 2),
            total_tds_deducted=round(total_tds, 2),
            duplicate_standard_deduction_warning=duplicate_std_ded,
            potential_tax_shortfall_warning=potential_shortfall,
            warnings=warnings,
        )
