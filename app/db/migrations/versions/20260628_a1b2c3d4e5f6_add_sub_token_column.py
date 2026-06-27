"""add sub_token column to users

Revision ID: a1b2c3d4e5f6
Revises: 7e8f9a0b1c2d
Create Date: 2026-06-28 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "7e8f9a0b1c2d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("sub_token", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_users_sub_token",
        "users",
        ["sub_token"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_users_sub_token", table_name="users")
    op.drop_column("users", "sub_token")