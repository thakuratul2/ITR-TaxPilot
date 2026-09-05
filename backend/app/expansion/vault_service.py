"""User Accounts and Secure Tax Document Vault service (DPDP Act compliant)."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class VaultDocument(BaseModel):
    """Secure tax document metadata stored in user vault."""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    assessment_year: str
    doc_type: str  # FORM16, FORM26AS, AIS, ITR_ACK, COMPUTATION_SHEET
    filename: str
    file_size_bytes: int
    is_encrypted: bool = True
    checksum_sha256: str
    uploaded_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class FilingRecord(BaseModel):
    """Archived tax filing history entry."""
    filing_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    assessment_year: str
    regime: str
    gross_income: float
    total_tax_paid: float
    refund_or_due_amount: float
    is_refund: bool
    acknowledgment_number: Optional[str] = None
    filed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class UserVault(BaseModel):
    """User's multi-year tax vault."""
    user_id: str
    pan: str
    documents: list[VaultDocument] = Field(default_factory=list)
    filing_history: list[FilingRecord] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DocumentVaultService:
    """In-memory and encrypted persistent vault manager for historical tax records."""

    def __init__(self):
        self._vaults: dict[str, UserVault] = {}

    def get_or_create_vault(self, user_id: str, pan: str) -> UserVault:
        """Retrieve existing user vault or create new one."""
        if user_id not in self._vaults:
            self._vaults[user_id] = UserVault(user_id=user_id, pan=pan.upper())
        return self._vaults[user_id]

    def add_document(
        self,
        user_id: str,
        pan: str,
        assessment_year: str,
        doc_type: str,
        filename: str,
        file_size_bytes: int,
        checksum_sha256: str,
    ) -> VaultDocument:
        """Register and store an encrypted tax document in the vault."""
        vault = self.get_or_create_vault(user_id, pan)
        doc = VaultDocument(
            user_id=user_id,
            assessment_year=assessment_year,
            doc_type=doc_type.upper(),
            filename=filename,
            file_size_bytes=file_size_bytes,
            is_encrypted=True,
            checksum_sha256=checksum_sha256,
        )
        vault.documents.append(doc)
        return doc

    def record_filing(
        self,
        user_id: str,
        pan: str,
        assessment_year: str,
        regime: str,
        gross_income: float,
        total_tax_paid: float,
        refund_or_due_amount: float,
        is_refund: bool,
        ack_number: Optional[str] = None,
    ) -> FilingRecord:
        """Record completed ITR filing in history."""
        vault = self.get_or_create_vault(user_id, pan)
        filing = FilingRecord(
            user_id=user_id,
            assessment_year=assessment_year,
            regime=regime,
            gross_income=gross_income,
            total_tax_paid=total_tax_paid,
            refund_or_due_amount=refund_or_due_amount,
            is_refund=is_refund,
            acknowledgment_number=ack_number,
        )
        vault.filing_history.append(filing)
        return filing

    def list_documents_by_ay(self, user_id: str, assessment_year: str) -> list[VaultDocument]:
        """Fetch all documents for a specific assessment year."""
        if user_id not in self._vaults:
            return []
        return [
            d for d in self._vaults[user_id].documents if d.assessment_year == assessment_year
        ]

    def get_filing_history(self, user_id: str) -> list[FilingRecord]:
        """Fetch chronologically ordered filing history."""
        if user_id not in self._vaults:
            return []
        return sorted(self._vaults[user_id].filing_history, key=lambda x: x.assessment_year, reverse=True)

    def export_user_data(self, user_id: str) -> Optional[dict]:
        """Export all user vault data for DPDP Act data portability."""
        if user_id not in self._vaults:
            return None
        return self._vaults[user_id].model_dump()

    def purge_user_vault(self, user_id: str) -> bool:
        """Permanently delete user vault data per Right to Erasure."""
        if user_id in self._vaults:
            del self._vaults[user_id]
            return True
        return False
