"""Income from House Property Calculation Sub-Engine (Section 22 to 27)."""

from app.calculator.models import HousePropertyInput, PropertyType
from app.tax.rules.base import TaxRegime


class HousePropertyEngine:
    """Deterministic House Property income and loss computation engine."""

    @classmethod
    def compute_house_property_income(
        cls,
        hp_input: HousePropertyInput,
        regime: TaxRegime,
    ) -> dict[str, float]:
        """
        Calculate net income or loss from house property for Old vs New regimes.
        """
        if hp_input.property_type == PropertyType.SELF_OCCUPIED:
            # Self-occupied property has NAV = 0
            gross_rent = 0.0
            municipal_taxes = 0.0
            nav = 0.0
            standard_deduction_24a = 0.0
            
            if regime == TaxRegime.OLD:
                # Under Old Regime, interest on SOP loan is allowed up to ₹2,00,000
                interest_24b = min(200000.0, hp_input.housing_loan_interest_sop)
                net_hp_income = -interest_24b
            else:
                # Under Section 115BAC (New Regime), SOP interest loss is disallowable (₹0)
                interest_24b = 0.0
                net_hp_income = 0.0

        else:
            # Let-out or Deemed let-out property
            gross_rent = hp_input.annual_lettable_value_or_rent
            municipal_taxes = hp_input.municipal_taxes_paid
            nav = max(0.0, gross_rent - municipal_taxes)
            
            # Statutory 30% standard deduction u/s 24(a)
            standard_deduction_24a = 0.30 * nav
            
            # Interest on housing loan for let-out property u/s 24(b)
            interest_24b = hp_input.housing_loan_interest_lop
            
            net_hp_income = nav - standard_deduction_24a - interest_24b
            
            # In New Regime, loss from let-out property cannot be set off against salary or other heads
            if regime == TaxRegime.NEW and net_hp_income < 0:
                net_hp_income = 0.0

        # Statutory set-off cap: Loss under house property can be set off against other heads up to max ₹2,00,000
        if net_hp_income < -200000.0:
            set_off_income = -200000.0
        else:
            set_off_income = net_hp_income

        return {
            "gross_annual_value": round(gross_rent, 2),
            "municipal_taxes_paid": round(municipal_taxes, 2),
            "net_annual_value": round(nav, 2),
            "standard_deduction_sec_24a": round(standard_deduction_24a, 2),
            "housing_loan_interest_sec_24b": round(interest_24b, 2),
            "net_house_property_income": round(set_off_income, 2),
        }
