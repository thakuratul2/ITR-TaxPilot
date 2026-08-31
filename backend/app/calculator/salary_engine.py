"""Salary Income Calculation Sub-Engine (Section 17, Section 10, Section 16)."""

from app.calculator.models import SalaryInput
from app.tax.rules.base import TaxRegime


class SalaryEngine:
    """Deterministic Salary income computation engine."""

    @staticmethod
    def calculate_hra_exemption(salary_input: SalaryInput) -> float:
        """
        Compute HRA exemption under Section 10(13A) read with Rule 2A.
        Exemption is least of:
          1. Actual HRA received
          2. Rent paid in excess of 10% of salary (Basic + DA)
          3. 50% of salary (if metro: Delhi, Mumbai, Kolkata, Chennai) or 40% of salary (non-metro)
        """
        hra_received = salary_input.hra_received
        rent_paid = salary_input.rent_paid_annual
        
        # Salary for HRA purposes = Basic + DA
        salary_for_hra = salary_input.basic_salary + salary_input.dearness_allowance
        
        # If no rent paid or rent paid <= 10% of salary, no exemption
        if rent_paid <= 0 or salary_for_hra <= 0 or hra_received <= 0:
            return 0.0

        limit_1_actual = hra_received
        limit_2_rent_excess = max(0.0, rent_paid - (0.10 * salary_for_hra))
        
        rate = 0.50 if salary_input.is_metro else 0.40
        limit_3_percent = rate * salary_for_hra

        exempt_hra = min(limit_1_actual, limit_2_rent_excess, limit_3_percent)
        return round(max(0.0, exempt_hra), 2)

    @staticmethod
    def calculate_entertainment_allowance(salary_input: SalaryInput) -> float:
        """
        Compute Entertainment Allowance deduction under Section 16(ii).
        Available ONLY to Government employees. Least of:
          1. ₹5,000
          2. 1/5th (20%) of Basic Salary
          3. Actual entertainment allowance received
        """
        if not salary_input.is_govt_employee or salary_input.entertainment_allowance <= 0:
            return 0.0

        limit_1_statutory = 5000.0
        limit_2_percent = 0.20 * salary_input.basic_salary
        limit_3_actual = salary_input.entertainment_allowance

        return round(min(limit_1_statutory, limit_2_percent, limit_3_actual), 2)

    @classmethod
    def compute_salary_income(
        cls,
        salary_input: SalaryInput,
        regime: TaxRegime,
        assessment_year: str = "2026-27",
    ) -> dict[str, float]:
        """
        Compute Net Salary Income across regimes for the specified Assessment Year.
        """
        # Determine total gross salary
        if salary_input.gross_salary_sec_17_1 > 0:
            gross_salary = (
                salary_input.gross_salary_sec_17_1
                + salary_input.perquisites_sec_17_2
                + salary_input.profits_in_lieu_sec_17_3
            )
        else:
            # Aggregate from line items
            gross_salary = (
                salary_input.basic_salary
                + salary_input.dearness_allowance
                + salary_input.hra_received
                + salary_input.lta_received
                + salary_input.entertainment_allowance
                + salary_input.perquisites_sec_17_2
                + salary_input.profits_in_lieu_sec_17_3
            )

        # Section 10 Allowances
        exempt_allowances = 0.0
        if regime == TaxRegime.OLD:
            exempt_hra = cls.calculate_hra_exemption(salary_input)
            exempt_lta = min(salary_input.lta_received, salary_input.lta_exempt)
            exempt_allowances = exempt_hra + exempt_lta + salary_input.other_exempt_allowances
            # Cannot exceed gross salary
            exempt_allowances = min(gross_salary, exempt_allowances)
        else:
            # Section 115BAC disallows HRA, LTA, and general Section 10 exemptions
            exempt_allowances = 0.0

        net_after_sec_10 = max(0.0, gross_salary - exempt_allowances)

        # Section 16 Deductions
        # Standard deduction u/s 16(ia):
        if regime == TaxRegime.NEW:
            # Budget 2024 increased Standard Deduction to ₹75,000 for AY 2026-27 & AY 2027-28
            std_ded_cap = 75000.0 if assessment_year in ["2026-27", "2027-28"] else 50000.0
        else:
            std_ded_cap = 50000.0

        std_deduction = min(net_after_sec_10, std_ded_cap)

        # Professional tax & entertainment allowance (Old Regime only)
        if regime == TaxRegime.OLD:
            prof_tax = min(2500.0, salary_input.professional_tax_paid)
            ent_allowance = cls.calculate_entertainment_allowance(salary_input)
        else:
            prof_tax = 0.0
            ent_allowance = 0.0

        total_sec_16 = std_deduction + prof_tax + ent_allowance
        net_salary_income = max(0.0, net_after_sec_10 - total_sec_16)

        return {
            "gross_salary": round(gross_salary, 2),
            "exempt_allowances_sec_10": round(exempt_allowances, 2),
            "standard_deduction_sec_16_ia": round(std_deduction, 2),
            "professional_tax_sec_16_iii": round(prof_tax, 2),
            "entertainment_allowance_sec_16_ii": round(ent_allowance, 2),
            "total_deductions_sec_16": round(total_sec_16, 2),
            "net_salary_income": round(net_salary_income, 2),
        }
