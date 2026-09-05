"""Advance Tax Shortfall & Interest Computation Sub-Engine (Section 234A, 234B, 234C)."""

import math
from datetime import date

from app.calculator.models import AdvanceTaxScheduleInput


class InterestEngine:
    """Deterministic Statutory Interest Calculator under Sections 234A, 234B, and 234C."""

    @classmethod
    def compute_interest_234abc(
        cls,
        total_tax_and_cess: float,
        relief_89: float,
        advance_tax: AdvanceTaxScheduleInput,
        assessment_year: str = "2026-27",
    ) -> dict[str, float]:
        """
        Compute interest under Sections 234A, 234B, and 234C.
        """
        # Assessed Tax under Section 234A/B/C
        tds_tcs = advance_tax.total_tds_tcs_deducted
        assessed_tax = max(0.0, total_tax_and_cess - relief_89 - tds_tcs)

        # If assessed tax is less than ₹10,000, taxpayer is not liable for advance tax
        if assessed_tax < 10000.0:
            return {
                "interest_234a": 0.0,
                "interest_234b": 0.0,
                "interest_234c": 0.0,
                "total_interest_234": 0.0,
                "assessed_tax": round(assessed_tax, 2),
            }

        # ---------------------------------------------------------
        # 1. Section 234C: Deferment of Advance Tax Installments
        # ---------------------------------------------------------
        # Cumulative advance tax paid by specific installment dates
        q1_paid = advance_tax.advance_tax_paid_q1_june15
        q2_paid = advance_tax.advance_tax_paid_q2_sept15
        q3_paid = advance_tax.advance_tax_paid_q3_dec15
        q4_paid = advance_tax.advance_tax_paid_q4_mar15

        int_234c = 0.0

        # Installment 1: June 15 (15% due; safe harbor is 12%)
        q1_due = 0.15 * assessed_tax
        if q1_paid < (0.12 * assessed_tax):
            shortfall_q1 = max(0.0, q1_due - q1_paid)
            int_234c += shortfall_q1 * 0.01 * 3  # 1% per month for 3 months

        # Installment 2: Sept 15 (45% due; safe harbor is 36%)
        q2_due = 0.45 * assessed_tax
        if q2_paid < (0.36 * assessed_tax):
            shortfall_q2 = max(0.0, q2_due - q2_paid)
            int_234c += shortfall_q2 * 0.01 * 3  # 1% per month for 3 months

        # Installment 3: Dec 15 (75% due)
        q3_due = 0.75 * assessed_tax
        if q3_paid < q3_due:
            shortfall_q3 = max(0.0, q3_due - q3_paid)
            int_234c += shortfall_q3 * 0.01 * 3  # 1% per month for 3 months

        # Installment 4: March 15 (100% due)
        q4_due = 1.00 * assessed_tax
        if q4_paid < q4_due:
            shortfall_q4 = max(0.0, q4_due - q4_paid)
            int_234c += shortfall_q4 * 0.01 * 1  # 1% for 1 month

        # ---------------------------------------------------------
        # 2. Section 234B: Default in Payment of Advance Tax
        # ---------------------------------------------------------
        # Applicable if total advance tax paid on or before 31st March < 90% of Assessed Tax
        total_adv_tax_paid_by_mar31 = max(q4_paid, advance_tax.advance_tax_paid_mar31)
        int_234b = 0.0

        if total_adv_tax_paid_by_mar31 < (0.90 * assessed_tax):
            shortfall_234b = max(0.0, assessed_tax - total_adv_tax_paid_by_mar31)
            # Default months: from 1st April of AY to date of filing/determination (e.g. July 31 = 4 months)
            filing_date = advance_tax.actual_filing_date or date(2026, 7, 31)
            start_date = date(filing_date.year, 4, 1)

            if filing_date > start_date:
                months_234b = math.ceil((filing_date - start_date).days / 30.0)
            else:
                months_234b = 4  # Default April to July = 4 months

            int_234b = shortfall_234b * 0.01 * months_234b

        # ---------------------------------------------------------
        # 3. Section 234A: Delay in Filing Return of Income
        # ---------------------------------------------------------
        int_234a = 0.0
        due_date = advance_tax.due_date_filing or date(2026, 7, 31)
        actual_date = advance_tax.actual_filing_date or due_date

        if actual_date > due_date:
            delay_days = (actual_date - due_date).days
            months_234a = math.ceil(delay_days / 30.0)
            tax_payable_for_234a = max(
                0.0,
                assessed_tax
                - total_adv_tax_paid_by_mar31
                - advance_tax.self_assessment_tax_paid,
            )
            int_234a = tax_payable_for_234a * 0.01 * months_234a

        total_int = int_234a + int_234b + int_234c

        return {
            "interest_234a": round(int_234a, 2),
            "interest_234b": round(int_234b, 2),
            "interest_234c": round(int_234c, 2),
            "total_interest_234": round(total_int, 2),
            "assessed_tax": round(assessed_tax, 2),
        }
