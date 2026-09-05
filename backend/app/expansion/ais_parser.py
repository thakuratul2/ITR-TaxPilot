"""Annual Information Statement (AIS / TIS) parser and financial data extractor."""

import json
from pydantic import BaseModel, Field


class SFTTransaction(BaseModel):
    """Statement of Financial Transaction line item."""
    information_code: str
    description: str
    source_reporting_entity: str
    amount: float
    reported_date: str = ""


class AISSummary(BaseModel):
    """Normalized AIS / TIS tax financial summary."""
    assessment_year: str
    pan: str
    savings_interest: float = 0.0
    term_deposit_interest: float = 0.0
    dividend_income: float = 0.0
    securities_sale_proceeds: float = 0.0
    mutual_fund_purchases: float = 0.0
    high_value_transactions: list[SFTTransaction] = Field(default_factory=list)
    total_tax_deducted_reported: float = 0.0


class AISParser:
    """Parser for Annual Information Statement (AIS) JSON and text payloads."""

    @classmethod
    def parse_ais_json(cls, json_str_or_dict: str | dict) -> AISSummary:
        """Parse structured AIS JSON payload from Income Tax Portal."""
        data = json.loads(json_str_or_dict) if isinstance(json_str_or_dict, str) else json_str_or_dict

        pan = data.get("pan", "ABCDE1234F")
        ay = data.get("assessment_year", "2025-26")

        savings_int = float(data.get("savings_bank_interest", 0.0))
        fd_int = float(data.get("fixed_deposit_interest", 0.0))
        dividends = float(data.get("dividend_income", 0.0))
        securities_sales = float(data.get("securities_sale_proceeds", 0.0))
        mf_purchases = float(data.get("mutual_fund_purchases", 0.0))
        tds_reported = float(data.get("total_tds_reported", 0.0))

        sft_items = []
        for sft in data.get("sft_transactions", []):
            sft_items.append(
                SFTTransaction(
                    information_code=sft.get("code", "SFT-001"),
                    description=sft.get("description", "Financial Transaction"),
                    source_reporting_entity=sft.get("reporting_entity", "Scheduled Bank"),
                    amount=float(sft.get("amount", 0.0)),
                    reported_date=sft.get("date", ""),
                )
            )

        return AISSummary(
            assessment_year=ay,
            pan=pan,
            savings_interest=savings_int,
            term_deposit_interest=fd_int,
            dividend_income=dividends,
            securities_sale_proceeds=securities_sales,
            mutual_fund_purchases=mf_purchases,
            high_value_transactions=sft_items,
            total_tax_deducted_reported=tds_reported,
        )
