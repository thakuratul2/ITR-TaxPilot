"""Initial schema: documents, jobs, analyses, tax_calculations

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-08-30 21:45:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Documents table
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("UPLOADED", "PROCESSING", "PARSED", "FAILED", "EXPIRED", name="documentstatus"),
            nullable=False,
        ),
        sa.Column("sha256_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Jobs table
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column(
            "job_type",
            sa.Enum("FORM16_EXTRACTION", "TAX_COMPUTATION", "REPORT_GENERATION", name="jobtype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="jobstatus"),
            nullable=False,
        ),
        sa.Column("progress_percentage", sa.Integer(), nullable=False),
        sa.Column("step_description", sa.String(length=255), nullable=True),
        sa.Column("result_id", sa.String(length=36), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Analyses table
    op.create_table(
        "analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_year", sa.String(length=10), nullable=False),
        sa.Column("financial_year", sa.String(length=10), nullable=True),
        sa.Column(
            "status",
            sa.Enum("IN_PROGRESS", "EXTRACTED", "CALCULATED", "FAILED", name="analysisstatus"),
            nullable=False,
        ),
        sa.Column("extracted_data", sa.JSON(), nullable=False),
        sa.Column("recommended_itr", sa.String(length=20), nullable=True),
        sa.Column("explanation", sa.String(length=5000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Tax Calculations table
    op.create_table(
        "tax_calculations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_year", sa.String(length=10), nullable=False),
        sa.Column("regime", sa.Enum("OLD", "NEW", name="taxregime"), nullable=False),
        sa.Column("gross_income", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_deductions", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("taxable_income", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tax_before_rebate", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("rebate_87a", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("cess", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_tax_liability", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tds_credit", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tax_payable", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("refund_due", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("calculation_breakdown", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tax_calculations")
    op.drop_table("analyses")
    op.drop_table("jobs")
    op.drop_table("documents")
