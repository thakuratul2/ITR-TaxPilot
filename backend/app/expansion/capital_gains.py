"""Capital Gains tax calculation and statement ingestion engine (Sec 111A, 112A, 112)."""

from enum import Enum
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    EQUITY_SHARE_LISTED = "EQUITY_SHARE_LISTED"
    EQUITY_MUTUAL_FUND = "EQUITY_MUTUAL_FUND"
    DEBT_MUTUAL_FUND = "DEBT_MUTUAL_FUND"
    UNLISTED_SHARE = "UNLISTED_SHARE"
    REAL_ESTATE = "REAL_ESTATE"


class HoldingType(str, Enum):
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"


class CapitalGainTransaction(BaseModel):
    """Single capital gain transaction item from broker statement (Zerodha, Groww, CAMS, etc.)."""
    isin: str = ""
    asset_name: str
    asset_type: AssetType = AssetType.EQUITY_SHARE_LISTED
    buy_date: str
    sell_date: str
    buy_value: float
    sell_value: float
    transfer_expenses: float = 0.0
    holding_type: HoldingType = HoldingType.SHORT_TERM
    net_gain_or_loss: float = 0.0


class CapitalGainsSummary(BaseModel):
    """Aggregated capital gains computation."""
    financial_year: str = "2024-25"
    stcg_sec111a_equity: float = 0.0      # Taxable at 20% (Budget 2024) / 15%
    stcg_other_slab: float = 0.0          # Taxable at normal slab rate
    ltcg_sec112a_equity: float = 0.0      # Listed equity above ₹1.25L exemption
    ltcg_sec112a_exempt_claimed: float = 0.0  # Up to ₹1,25,000 exemption
    ltcg_other_sec112: float = 0.0        # Taxable at 12.5% / 20%
    total_stcg: float = 0.0
    total_ltcg: float = 0.0
    total_capital_gains_tax: float = 0.0
    requires_itr2_or_itr3: bool = True


class CapitalGainsEngine:
    """Calculates capital gains tax liability adhering to Income Tax Act rules (FY 2024-25 / AY 2025-26)."""

    LTCG_112A_EXEMPTION_LIMIT: float = 125000.0  # ₹1.25 Lakh per AY 2025-26 Budget
    STCG_111A_RATE: float = 0.20                 # 20% post July 2024
    LTCG_112A_RATE: float = 0.125                # 12.5% post July 2024
    LTCG_112_RATE: float = 0.125                 # 12.5%

    @classmethod
    def compute_gains(
        cls,
        transactions: list[CapitalGainTransaction],
        financial_year: str = "2024-25",
    ) -> CapitalGainsSummary:
        """Compute aggregated STCG and LTCG across portfolio transactions."""
        stcg_111a = 0.0
        stcg_other = 0.0
        ltcg_112a_raw = 0.0
        ltcg_other = 0.0

        for tx in transactions:
            gain = (tx.sell_value - tx.buy_value) - tx.transfer_expenses

            if tx.holding_type == HoldingType.SHORT_TERM:
                if tx.asset_type in (AssetType.EQUITY_SHARE_LISTED, AssetType.EQUITY_MUTUAL_FUND):
                    stcg_111a += gain
                else:
                    stcg_other += gain
            else:  # LONG_TERM
                if tx.asset_type in (AssetType.EQUITY_SHARE_LISTED, AssetType.EQUITY_MUTUAL_FUND):
                    ltcg_112a_raw += gain
                else:
                    ltcg_other += gain

        # Calculate LTCG 112A exemption (₹1.25 Lakh)
        ltcg_112a_taxable = 0.0
        ltcg_112a_exempt = 0.0
        if ltcg_112a_raw > 0:
            ltcg_112a_exempt = min(ltcg_112a_raw, cls.LTCG_112A_EXEMPTION_LIMIT)
            ltcg_112a_taxable = max(0.0, ltcg_112a_raw - cls.LTCG_112A_EXEMPTION_LIMIT)

        # Tax calculation
        tax_stcg_111a = max(0.0, stcg_111a) * cls.STCG_111A_RATE
        tax_ltcg_112a = ltcg_112a_taxable * cls.LTCG_112A_RATE
        tax_ltcg_112 = max(0.0, ltcg_other) * cls.LTCG_112_RATE

        total_tax = tax_stcg_111a + tax_ltcg_112a + tax_ltcg_112
        # Cess 4%
        total_tax_with_cess = total_tax * 1.04

        total_stcg = stcg_111a + stcg_other
        total_ltcg = ltcg_112a_raw + ltcg_other
        has_gains = (total_stcg != 0 or total_ltcg != 0)

        return CapitalGainsSummary(
            financial_year=financial_year,
            stcg_sec111a_equity=round(stcg_111a, 2),
            stcg_other_slab=round(stcg_other, 2),
            ltcg_sec112a_equity=round(ltcg_112a_taxable, 2),
            ltcg_sec112a_exempt_claimed=round(ltcg_112a_exempt, 2),
            ltcg_other_sec112=round(ltcg_other, 2),
            total_stcg=round(total_stcg, 2),
            total_ltcg=round(total_ltcg, 2),
            total_capital_gains_tax=round(total_tax_with_cess, 2),
            requires_itr2_or_itr3=has_gains,
        )
