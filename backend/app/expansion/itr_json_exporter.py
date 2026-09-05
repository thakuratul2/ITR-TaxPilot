"""CBDT e-filing JSON schema generator and export module for ITR-1 (Sahaj) and ITR-2."""

import json
from pydantic import BaseModel, Field
from app.tax.rules.base import TaxRegime


class PersonalInfo(BaseModel):
    pan: str
    first_name: str
    middle_name: str = ""
    last_name: str
    dob: str  # YYYY-MM-DD
    aadhaar_number: str = ""
    mobile: str
    email: str
    address_line: str = ""
    city: str = ""
    state: str = ""
    pincode: str = ""


class BankAccount(BaseModel):
    account_number: str
    ifsc_code: str
    bank_name: str
    account_type: str = "SAVINGS"  # SAVINGS / CURRENT
    selected_for_refund: bool = True


class ITR1ExportPayload(BaseModel):
    """CBDT Compliant ITR-1 (Sahaj) JSON Schema representation."""
    form_name: str = "ITR-1"
    assessment_year: str = "2025-26"
    regime_selected: TaxRegime = TaxRegime.NEW
    personal_info: PersonalInfo
    gross_salary: float
    standard_deduction: float
    income_from_salary: float
    income_from_other_sources: float = 0.0
    gross_total_income: float
    total_deductions_chapter_via: float = 0.0
    total_taxable_income: float
    total_tax_computed: float
    rebate_87a: float = 0.0
    health_and_education_cess: float = 0.0
    total_tax_liability: float
    total_tds_claimed: float = 0.0
    total_advance_tax_paid: float = 0.0
    net_tax_payable_or_refund: float
    is_refund: bool = False
    bank_accounts: list[BankAccount] = Field(default_factory=list)


class ITRJSONExporter:
    """Exports and validates standardized CBDT JSON e-filing payloads."""

    @classmethod
    def generate_itr1_json(cls, payload: ITR1ExportPayload) -> dict:
        """Convert ITR1ExportPayload into official CBDT schema dict."""
        schema_dict = {
            "ITR": {
                "ITR1": {
                    "CreationInfo": {
                        "SWVersionNo": "ITR-TaxPilot v1.0",
                        "SWCreatedBy": "ITR-TaxPilot Engine",
                        "JSONCreatedDate": "2026-09-05",
                    },
                    "Form_ITR1": {
                        "FormName": "ITR-1",
                        "AssessmentYear": payload.assessment_year,
                        "OptOutNewRegime": "N" if payload.regime_selected == TaxRegime.NEW else "Y",
                    },
                    "PersonalInfo": {
                        "PAN": payload.personal_info.pan.upper(),
                        "AssesseeName": {
                            "FirstName": payload.personal_info.first_name,
                            "SurNameOrOrgName": payload.personal_info.last_name,
                        },
                        "DOB": payload.personal_info.dob,
                        "AadhaarCardNo": payload.personal_info.aadhaar_number,
                        "Address": {
                            "ResidenceNo": payload.personal_info.address_line,
                            "CityOrTownOrDistrict": payload.personal_info.city,
                            "StateCode": payload.personal_info.state,
                            "PinCode": payload.personal_info.pincode,
                            "MobileNo": payload.personal_info.mobile,
                            "EmailAddress": payload.personal_info.email,
                        },
                    },
                    "IncomeDeductions": {
                        "GrossSalary": payload.gross_salary,
                        "DeductionUs16ia": payload.standard_deduction,
                        "IncomeFromSal": payload.income_from_salary,
                        "IncomeOthSrc": payload.income_from_other_sources,
                        "GrossTotIncome": payload.gross_total_income,
                        "UsrDeductUndChapVIA": {
                            "TotalChapVIADeductions": payload.total_deductions_chapter_via
                        },
                        "TotalIncome": payload.total_taxable_income,
                    },
                    "TaxComputation": {
                        "TotalTaxPayable": payload.total_tax_computed,
                        "Rebate87A": payload.rebate_87a,
                        "HealthAndEducationCess": payload.health_and_education_cess,
                        "TotalTaxLiability": payload.total_tax_liability,
                        "TotalTDSClaimed": payload.total_tds_claimed,
                        "TotalAdvanceTaxPaid": payload.total_advance_tax_paid,
                        "RefundDue": abs(payload.net_tax_payable_or_refund) if payload.is_refund else 0.0,
                        "BalanceTaxPayable": payload.net_tax_payable_or_refund if not payload.is_refund else 0.0,
                    },
                    "BankAccountDetails": [
                        {
                            "BankName": b.bank_name,
                            "IFSCCode": b.ifsc_code.upper(),
                            "BankAccountNo": b.account_number,
                            "AccountType": b.account_type,
                            "UseForRefund": "Y" if b.selected_for_refund else "N",
                        }
                        for b in payload.bank_accounts
                    ],
                }
            }
        }
        return schema_dict

    @classmethod
    def validate_schema(cls, schema_dict: dict) -> list[str]:
        """Validate generated CBDT JSON schema for mandatory tags."""
        errors = []
        if "ITR" not in schema_dict or "ITR1" not in schema_dict["ITR"]:
            return ["Invalid root schema: missing ITR -> ITR1 hierarchy."]

        itr1 = schema_dict["ITR"]["ITR1"]

        pan = itr1.get("PersonalInfo", {}).get("PAN", "")
        if not pan or len(pan) != 10:
            errors.append(f"Invalid PAN length: '{pan}'. Expected 10 characters.")

        bank_details = itr1.get("BankAccountDetails", [])
        if not bank_details:
            errors.append("At least one Bank Account is required for CBDT e-filing verification.")
        else:
            for b in bank_details:
                if len(b.get("IFSCCode", "")) != 11:
                    errors.append(f"Invalid IFSC code '{b.get('IFSCCode')}'. Expected 11 alphanumeric characters.")

        return errors

    @classmethod
    def export_to_json_string(cls, payload: ITR1ExportPayload, indent: int = 2) -> str:
        """Export payload to formatted JSON string."""
        data = cls.generate_itr1_json(payload)
        return json.dumps(data, indent=indent)
