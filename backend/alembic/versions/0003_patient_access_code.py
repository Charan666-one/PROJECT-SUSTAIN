"""add patient portal access_code

Revision ID: 0003_patient_access_code
Revises: 0002_dob_optional
Create Date: 2026-08-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_patient_access_code"
down_revision = "0002_dob_optional"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("access_code", sa.String(length=12), nullable=True))


def downgrade() -> None:
    op.drop_column("patients", "access_code")
