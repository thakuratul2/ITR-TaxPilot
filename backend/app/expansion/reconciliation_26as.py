"""Form 26AS tax credit reconciliation module against Form 16 Part A and advance tax records."""

from pydantic import BaseModel, Field


class TDSEntry(BaseModel):
    """Tax Deducted at Source entry in Form 26AS or Form 16 Part A."""
    deductor_tan: str
    deductor_name: str
    total_amount_paid: float
    total_tds_deducted: float
    total_tds_deposited: float
    section: str = "192"  # e.g., 192 for Salary, 194A for Interest


class Form26ASData(BaseModel):
    """Normalized Form 26AS Tax Credit Statement."""
    pan: str
    assessment_year: str
    financial_year: str
    part_a_tds_salary: list[TDSEntry] = Field(default_factory=list)
    part_a1_tds_other: list[TDSEntry] = Field(default_factory=list)
    part_c_advance_tax: float = 0.0
    part_c_self_assessment_tax: float = 0.0
    total_tax_credits: float = 0.0


class ReconciliationMismatch(BaseModel):
    """Discrepancy between Form 16 Part A and Form 26AS."""
    deductor_tan: str
    deductor_name: str
    form16_tds: float
    form26as_tds: float
    difference: float
    description: str
    severity: str = "WARNING"  # CRITICAL, WARNING, INFO


class ReconciliationReport(BaseModel):
    """Final reconciliation report comparing Form 16 and Form 26AS."""
    pan: str
    assessment_year: str
    total_form16_tds: float
    total_26as_tds: float
    total_advance_tax_claimed: float
    mismatches: list[ReconciliationMismatch] = Field(default_factory=list)
    is_fully_reconciled: bool
    actionable_advice: list[str] = Field(default_factory=list)


class TaxCreditReconciler:
    """Reconciles employer Form 16 TDS with CBDT Form 26AS records."""

    @classmethod
    def reconcile(
        cls,
        form16_tds_entries: list[TDSEntry],
        form_26as: Form26ASData,
        tolerance: float = 1.0,
    ) -> ReconciliationReport:
        """Reconcile Form 16 TDS entries against 26AS."""
        total_form16_tds = sum(e.total_tds_deposited for e in form16_tds_entries)
        total_26as_tds = sum(e.total_tds_deposited for e in form_26as.part_a_tds_salary) + sum(
            e.total_tds_deposited for e in form_26as.part_a1_tds_other
        )

        mismatches: list[ReconciliationMismatch] = []
        advice: list[str] = []

        # Map 26AS by TAN
        as26_by_tan = {e.deductor_tan.upper(): e for e in form_26as.part_a_tds_salary}

        for f16_entry in form16_tds_entries:
            tan = f16_entry.deductor_tan.upper()
            if tan in as26_by_tan:
                matched_26as = as26_by_tan[tan]
                diff = abs(f16_entry.total_tds_deposited - matched_26as.total_tds_deposited)
                if diff > tolerance:
                    if matched_26as.total_tds_deposited < f16_entry.total_tds_deposited:
                        mismatches.append(
                            ReconciliationMismatch(
                                deductor_tan=tan,
                                deductor_name=f16_entry.deductor_name,
                                form16_tds=f16_entry.total_tds_deposited,
                                form26as_tds=matched_26as.total_tds_deposited,
                                difference=diff,
                                description=(
                                    f"Form 26AS reflects ₹{matched_26as.total_tds_deposited:,.2f} TDS, "
                                    f"which is less than Form 16 (₹{f16_entry.total_tds_deposited:,.2f})."
                                ),
                                severity="CRITICAL",
                            )
                        )
                        advice.append(
                            f"Contact employer ({f16_entry.deductor_name}) to file revised quarterly TDS return (Form 24Q)."
                        )
            else:
                mismatches.append(
                    ReconciliationMismatch(
                        deductor_tan=tan,
                        deductor_name=f16_entry.deductor_name,
                        form16_tds=f16_entry.total_tds_deposited,
                        form26as_tds=0.0,
                        difference=f16_entry.total_tds_deposited,
                        description=f"TAN {tan} not found in Form 26AS TDS records.",
                        severity="CRITICAL",
                    )
                )
                advice.append(
                    f"Employer TAN {tan} has not deposited TDS or PAN was misreported in Form 24Q."
                )

        is_reconciled = len(mismatches) == 0

        if is_reconciled:
            advice.append("All Form 16 TDS entries perfectly match Form 26AS tax credits.")

        return ReconciliationReport(
            pan=form_26as.pan,
            assessment_year=form_26as.assessment_year,
            total_form16_tds=round(total_form16_tds, 2),
            total_26as_tds=round(total_26as_tds, 2),
            total_advance_tax_claimed=round(form_26as.part_c_advance_tax + form_26as.part_c_self_assessment_tax, 2),
            mismatches=mismatches,
            is_fully_reconciled=is_reconciled,
            actionable_advice=advice,
        )
