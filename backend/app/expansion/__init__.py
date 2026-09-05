"""Expansion and post-MVP capabilities package."""

from app.expansion.ais_parser import AISParser, AISSummary, SFTTransaction
from app.expansion.capital_gains import (
    AssetType,
    CapitalGainTransaction,
    CapitalGainsEngine,
    CapitalGainsSummary,
    HoldingType,
)
from app.expansion.itr_json_exporter import (
    BankAccount,
    ITR1ExportPayload,
    ITRJSONExporter,
    PersonalInfo,
)
from app.expansion.multi_form16_aggregator import (
    AggregatedSalaryProfile,
    EmployerForm16Input,
    MultiForm16Aggregator,
)
from app.expansion.reconciliation_26as import (
    Form26ASData,
    ReconciliationMismatch,
    ReconciliationReport,
    TaxCreditReconciler,
    TDSEntry,
)
from app.expansion.vault_service import (
    DocumentVaultService,
    FilingRecord,
    UserVault,
    VaultDocument,
)

__all__ = [
    "AISParser",
    "AISSummary",
    "SFTTransaction",
    "TDSEntry",
    "Form26ASData",
    "ReconciliationMismatch",
    "ReconciliationReport",
    "TaxCreditReconciler",
    "AssetType",
    "HoldingType",
    "CapitalGainTransaction",
    "CapitalGainsSummary",
    "CapitalGainsEngine",
    "EmployerForm16Input",
    "AggregatedSalaryProfile",
    "MultiForm16Aggregator",
    "PersonalInfo",
    "BankAccount",
    "ITR1ExportPayload",
    "ITRJSONExporter",
    "VaultDocument",
    "FilingRecord",
    "UserVault",
    "DocumentVaultService",
]
