"""make patient date_of_birth optional

Revision ID: 0002_dob_optional
Revises: 2de9b8fd4ba5
Create Date: 2026-08-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_dob_optional"
down_revision = "2de9b8fd4ba5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("patients", "date_of_birth", existing_type=sa.Date(), nullable=True)


def downgrade() -> None:
    op.alter_column("patients", "date_of_birth", existing_type=sa.Date(), nullable=False)
