"""Chapter VI-A Deductions Aggregator Sub-Engine."""

from app.calculator.models import ChapterVIAInput, OtherSourcesInput, SeniorCitizenCategory
from app.tax.rules.base import TaxRegime


class DeductionEngine:
    """Deterministic Chapter VI-A Deductions computation engine."""

    @staticmethod
    def calculate_section_80d(
        ch_input: ChapterVIAInput,
        category: SeniorCitizenCategory,
    ) -> float:
        """
        Compute Section 80D Health Insurance deduction.
        - Self, spouse, children: ₹25,000 (₹50,000 if self is senior)
        - Parents: ₹25,000 (₹50,000 if parents are senior)
        - Preventive checkup: Max ₹5,000 overall within limits
        """
        self_is_senior = category in [SeniorCitizenCategory.SENIOR_CITIZEN, SeniorCitizenCategory.SUPER_SENIOR]
        self_cap = 50000.0 if self_is_senior else 25000.0
        parents_cap = 50000.0 if ch_input.parents_are_senior_citizens else 25000.0

        preventive_claimed = min(5000.0, ch_input.section_80d_preventive)
        
        # Allocate preventive to self first
        self_premium = ch_input.section_80d_self
        self_allowed = min(self_cap, self_premium + preventive_claimed)
        preventive_used_in_self = max(0.0, self_allowed - self_premium)
        
        # Remaining preventive checkup if any to parents
        remaining_preventive = max(0.0, preventive_claimed - preventive_used_in_self)
        parents_premium = ch_input.section_80d_parents
        parents_allowed = min(parents_cap, parents_premium + remaining_preventive)

        return round(self_allowed + parents_allowed, 2)

    @classmethod
    def compute_chapter_via_deductions(
        cls,
        ch_input: ChapterVIAInput,
        os_input: OtherSourcesInput,
        gross_total_income: float,
        regime: TaxRegime,
        category: SeniorCitizenCategory = SeniorCitizenCategory.INDIVIDUAL,
    ) -> dict[str, any]:
        """
        Compute all eligible Chapter VI-A deductions and return itemized breakdown.
        """
        itemized: dict[str, float] = {}

        if regime == TaxRegime.NEW:
            # Under Section 115BAC (New Regime), ONLY Section 80CCD(2) is allowed
            if ch_input.section_80ccd_2 > 0:
                # Employer NPS contribution
                itemized["80CCD(2)"] = round(ch_input.section_80ccd_2, 2)
            
            total_deductions = sum(itemized.values())
            # Cannot exceed Gross Total Income
            total_allowed = min(gross_total_income, total_deductions)
            return {
                "total_deductions": round(total_allowed, 2),
                "itemized": itemized,
            }

        # --- OLD TAX REGIME DEDUCTIONS ---

        # 1. Section 80CCE Aggregate Cap (80C + 80CCC + 80CCD(1) <= ₹1,50,000)
        cce_pool = ch_input.section_80c + ch_input.section_80ccc + ch_input.section_80ccd_1
        cce_allowed = min(150000.0, cce_pool)
        if cce_allowed > 0:
            itemized["80CCE (80C/80CCC/80CCD(1))"] = round(cce_allowed, 2)

        # 2. Section 80CCD(1B) - Additional NPS (Exclusive ₹50,000)
        if ch_input.section_80ccd_1b > 0:
            nps_1b_allowed = min(50000.0, ch_input.section_80ccd_1b)
            itemized["80CCD(1B)"] = round(nps_1b_allowed, 2)

        # 3. Section 80CCD(2) - Employer NPS Contribution
        if ch_input.section_80ccd_2 > 0:
            itemized["80CCD(2)"] = round(ch_input.section_80ccd_2, 2)

        # 4. Section 80D - Health Insurance & Preventive Checkup
        ded_80d = cls.calculate_section_80d(ch_input, category)
        if ded_80d > 0:
            itemized["80D"] = round(ded_80d, 2)

        # 5. Section 80E - Education Loan Interest (No Cap)
        if ch_input.section_80e > 0:
            itemized["80E"] = round(ch_input.section_80e, 2)

        # 6. Section 80EEA & 80EEB
        if ch_input.section_80eea > 0:
            itemized["80EEA"] = round(min(150000.0, ch_input.section_80eea), 2)
        if ch_input.section_80eeb > 0:
            itemized["80EEB"] = round(min(150000.0, ch_input.section_80eeb), 2)

        # 7. Section 80TTA / 80TTB
        is_senior = category in [SeniorCitizenCategory.SENIOR_CITIZEN, SeniorCitizenCategory.SUPER_SENIOR]
        if is_senior:
            # 80TTB allows interest on all deposits up to ₹50,000
            total_interest = os_input.savings_bank_interest + os_input.fixed_deposit_interest
            actual_ttb = max(ch_input.section_80ttb, total_interest)
            ttb_allowed = min(50000.0, actual_ttb)
            if ttb_allowed > 0:
                itemized["80TTB"] = round(ttb_allowed, 2)
        else:
            # 80TTA allows savings bank interest up to ₹10,000
            actual_tta = max(ch_input.section_80tta, os_input.savings_bank_interest)
            tta_allowed = min(10000.0, actual_tta)
            if tta_allowed > 0:
                itemized["80TTA"] = round(tta_allowed, 2)

        # 8. Section 80G - Donations
        g_100_no = ch_input.section_80g_100_no_limit
        g_50_no = 0.50 * ch_input.section_80g_50_no_limit
        
        # Qualifying limit for 80G is 10% of Adjusted Gross Total Income
        adjusted_gti = max(0.0, gross_total_income - cce_allowed - ded_80d)
        qualifying_limit = 0.10 * adjusted_gti
        
        qualifying_pool = ch_input.section_80g_100_qualifying + (0.50 * ch_input.section_80g_50_qualifying)
        g_qualifying_allowed = min(qualifying_limit, qualifying_pool)
        
        total_80g = g_100_no + g_50_no + g_qualifying_allowed
        if total_80g > 0:
            itemized["80G"] = round(total_80g, 2)

        # 9. Other Specific Sections (80U, 80DD, 80DDB, 80GG)
        if ch_input.section_80u > 0:
            itemized["80U"] = round(ch_input.section_80u, 2)
        if ch_input.section_80dd > 0:
            itemized["80DD"] = round(ch_input.section_80dd, 2)
        if ch_input.section_80ddb > 0:
            itemized["80DDB"] = round(ch_input.section_80ddb, 2)
        if ch_input.section_80gg > 0:
            itemized["80GG"] = round(min(60000.0, ch_input.section_80gg), 2)

        # Total Aggregated Deductions cannot exceed Gross Total Income
        gross_deductions = sum(itemized.values())
        total_allowed = min(gross_total_income, gross_deductions)

        return {
            "total_deductions": round(total_allowed, 2),
            "itemized": itemized,
        }
