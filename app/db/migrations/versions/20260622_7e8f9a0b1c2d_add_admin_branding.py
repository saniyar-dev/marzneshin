"""add admin branding columns

Revision ID: 7e8f9a0b1c2d
Revises: 57eba0a293f2
Create Date: 2026-06-22 04:05:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7e8f9a0b1c2d"
down_revision = "57eba0a293f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "admins",
        sa.Column("brand_shop_name", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "admins",
        sa.Column("brand_logo_filename", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "admins",
        sa.Column("brand_support_url", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("admins", "brand_support_url")
    op.drop_column("admins", "brand_logo_filename")
    op.drop_column("admins", "brand_shop_name")
