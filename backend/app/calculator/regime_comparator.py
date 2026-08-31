"""Side-by-side Regime Comparison and Recommendation Sub-Engine."""

from app.calculator.models import RegimeComparisonResult, RegimeComputation, TaxpayerProfileInput


class RegimeComparator:
    """Deterministic Old vs New Tax Regime Comparator."""

    @staticmethod
    def round_to_nearest_10(amount: float) -> float:
        """Statutory rounding to nearest multiple of ₹10 under Sections 288A & 288B."""
        return float(round(amount / 10.0) * 10)

    @classmethod
    def compare(
        cls,
        old_regime: RegimeComputation,
        new_regime: RegimeComputation,
        profile: TaxpayerProfileInput,
    ) -> RegimeComparisonResult:
        """
        Compare computations, select optimal tax regime, and generate itemized breakdown.
        """
        old_tax = old_regime.aggregate_liability
        new_tax = new_regime.aggregate_liability

        if new_tax <= old_tax:
            recommended = "NEW"
            savings = old_tax - new_tax
            percentage_savings = (savings / old_tax * 100.0) if old_tax > 0 else 0.0
        else:
            recommended = "OLD"
            savings = new_tax - old_tax
            percentage_savings = (savings / new_tax * 100.0) if new_tax > 0 else 0.0

        deduction_diff = (
            old_regime.total_chapter_via_deductions
            + old_regime.exempt_allowances_sec_10
            + old_regime.professional_tax_sec_16_iii
        ) - (
            new_regime.total_chapter_via_deductions
            + new_regime.exempt_allowances_sec_10
        )

        slab_tax_diff = old_regime.base_tax_on_income - new_regime.base_tax_on_income

        # Recommend ITR Form
        # ITR-1 Sahaj is valid if Total Income <= ₹50 Lakhs, has 1 House Property (SOP), no business income
        is_single_sop = profile.house_property.annual_lettable_value_or_rent <= 0
        total_inc = max(old_regime.total_taxable_income, new_regime.total_taxable_income)
        
        if total_inc <= 5000000.0 and is_single_sop:
            recommended_itr = "ITR-1 (Sahaj)"
        else:
            recommended_itr = "ITR-2"

        # Generate summary explanation
        if recommended == "NEW":
            if savings > 0:
                explanation = (
                    f"The New Tax Regime (Section 115BAC) is more beneficial for AY {profile.assessment_year}, "
                    f"saving you ₹{savings:,.0f} ({percentage_savings:.1f}% reduction) due to lower progressive slab rates "
                    f"and an enhanced Standard Deduction of ₹75,000."
                )
            else:
                explanation = (
                    f"Both regimes yield identical zero tax liability for AY {profile.assessment_year}. "
                    f"The New Tax Regime is recommended as the statutory default."
                )
        else:
            explanation = (
                f"The Old Tax Regime is more beneficial for AY {profile.assessment_year}, "
                f"saving you ₹{savings:,.0f} ({percentage_savings:.1f}% reduction) because your itemized Chapter VI-A "
                f"deductions and Section 10 exemptions total ₹{old_regime.total_chapter_via_deductions + old_regime.exempt_allowances_sec_10:,.0f}."
            )

        return RegimeComparisonResult(
            assessment_year=profile.assessment_year,
            recommended_regime=recommended,
            tax_savings_amount=round(savings, 2),
            percentage_savings=round(percentage_savings, 2),
            old_regime=old_regime,
            new_regime=new_regime,
            deduction_difference=round(deduction_diff, 2),
            slab_tax_difference=round(slab_tax_diff, 2),
            recommended_itr_form=recommended_itr,
            explanation=explanation,
        )
