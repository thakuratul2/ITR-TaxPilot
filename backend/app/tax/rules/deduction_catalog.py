"""Chapter VI-A deduction eligibility catalog across regimes and Assessment Years."""

from dataclasses import dataclass


@dataclass
class DeductionInfo:
    """Detailed information about a specific deduction section."""
    section: str
    name: str
    description: str
    max_limit: float | None = None  # None if no limit
    applicable_regimes: list[str] = None  # ["OLD", "NEW"] or ["OLD"] or ["NEW"]
    requires_documents: bool = False
    notes: str = ""


class DeductionCatalog:
    """Catalog of Chapter VI-A deductions with regime-wise eligibility."""

    def __init__(self):
        self.deductions: dict[str, DeductionInfo] = {
            # Section 80C Group
            "80C": DeductionInfo(
                section="80C",
                name="Section 80C - Investments & Expenses",
                description="Life insurance, PPF, EPF, ELSS, tuition fees, home loan principal repayment, etc.",
                max_limit=150000,
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="Combined limit of ₹1.5L across all 80C sub-sections",
            ),
            "80CCC": DeductionInfo(
                section="80CCC",
                name="Section 80CCC - Pension Funds",
                description="Contribution to pension fund of LIC or other approved insurer",
                max_limit=150000,  # Part of 80C limit
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="Within overall 80C limit",
            ),
            "80CCD(1)": DeductionInfo(
                section="80CCD(1)",
                name="Section 80CCD(1) - NPS (Employee)",
                description="Employee's contribution to NPS",
                max_limit=50000,  # Additional over 80C
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="Additional ₹50K over 80C limit",
            ),
            "80CCD(1B)": DeductionInfo(
                section="80CCD(1B)",
                name="Section 80CCD(1B) - NPS (Additional)",
                description="Additional contribution to NPS for central government employees",
                max_limit=50000,
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="Separate ₹50K limit for government employees",
            ),
            "80CCD(2)": DeductionInfo(
                section="80CCD(2)",
                name="Section 80CCD(2) - NPS (Employer)",
                description="Employer's contribution to NPS",
                max_limit=None,  # Up to 14% of salary
                applicable_regimes=["OLD", "NEW"],
                requires_documents=True,
                notes="Available under both regimes",
            ),

            # Health Insurance
            "80D": DeductionInfo(
                section="80D",
                name="Section 80D - Health Insurance Premium",
                description="Health insurance premium for self, family, and parents",
                max_limit=100000,  # Higher for senior citizen parents
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="₹25K for self/family, ₹25K for parents (₹50K if senior citizens)",
            ),

            # Education Loan
            "80E": DeductionInfo(
                section="80E",
                name="Section 80E - Education Loan Interest",
                description="Interest on education loan for higher studies",
                max_limit=None,  # No upper limit
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="Available for 8 years from start of repayment",
            ),

            # Donations
            "80G": DeductionInfo(
                section="80G",
                name="Section 80G - Donations",
                description="Donations to specified funds and charitable institutions",
                max_limit=None,  # Varies by recipient
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="50% or 100% deduction based on recipient",
            ),

            # Interest Income
            "80TTA": DeductionInfo(
                section="80TTA",
                name="Section 80TTA - Savings Interest",
                description="Interest on savings account (non-senior citizens)",
                max_limit=10000,
                applicable_regimes=["OLD"],
                requires_documents=False,
                notes="₹10K limit for individuals below 60 years",
            ),
            "80TTB": DeductionInfo(
                section="80TTB",
                name="Section 80TTB - Senior Citizen Interest",
                description="Interest on deposits for senior citizens",
                max_limit=50000,
                applicable_regimes=["OLD"],
                requires_documents=False,
                notes="₹50K limit for senior citizens (60+ years)",
            ),

            # Housing Loan Interest
            "24(b)": DeductionInfo(
                section="24(b)",
                name="Section 24(b) - Home Loan Interest",
                description="Interest on housing loan for self-occupied property",
                max_limit=200000,  # For loans after 1.4.1999
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="₹2L limit for self-occupied, no limit for let-out property",
            ),
            "80EE": DeductionInfo(
                section="80EE",
                name="Section 80EE - First-Time Home Buyer",
                description="Additional interest deduction for first-time home buyers",
                max_limit=50000,
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="Available for loans up to ₹35L with property value ≤ ₹50L",
            ),
            "80EEA": DeductionInfo(
                section="80EEA",
                name="Section 80EEA - Affordable Housing",
                description="Additional interest deduction for affordable housing",
                max_limit=150000,
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="For first-time buyers with loan ≤ ₹25L and property value ≤ ₹45L",
            ),
            "80EEB": DeductionInfo(
                section="80EEB",
                name="Section 80EEB - Additional Home Loan Interest",
                description="Additional interest deduction for home loans",
                max_limit=150000,
                applicable_regimes=["OLD"],
                requires_documents=True,
                notes="For home loans taken between 1.4.2019 to 31.3.2020",
            ),

            # Presumptive Taxation
            "44AA": DeductionInfo(
                section="44AA",
                name="Section 44AA - Maintenance of Books",
                description="Maintenance of books of accounts for certain professions",
                max_limit=None,
                applicable_regimes=["OLD", "NEW"],
                requires_documents=True,
                notes="Presumptive taxation provisions",
            ),
            "44ADA": DeductionInfo(
                section="44ADA",
                name="Section 44ADA - Presumptive Income for Professionals",
                description="50% of gross receipts is deemed as income for professionals",
                max_limit=50000000,  # Up to ₹50L gross receipts
                applicable_regimes=["OLD", "NEW"],
                requires_documents=True,
                notes="Available for eligible professionals",
            ),
        }

    def get_deduction_info(self, section: str) -> DeductionInfo | None:
        """Get detailed information about a specific deduction section."""
        return self.deductions.get(section)

    def is_eligible(self, section: str, regime: str) -> bool:
        """Check if a deduction is eligible under the specified regime."""
        deduction = self.get_deduction_info(section)
        if not deduction:
            return False
        return regime in deduction.applicable_regimes

    def list_eligible_deductions(self, regime: str) -> list[DeductionInfo]:
        """List all deductions eligible under the specified regime."""
        return [
            deduction for deduction in self.deductions.values()
            if regime in deduction.applicable_regimes
        ]

    def get_all_sections(self) -> list[str]:
        """Get list of all deduction sections in the catalog."""
        return sorted(self.deductions.keys())


# Global catalog instance
deduction_catalog = DeductionCatalog()
