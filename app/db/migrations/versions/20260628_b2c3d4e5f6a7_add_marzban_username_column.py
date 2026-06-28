"""add marzban_username column to users

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-28 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("marzban_username", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_users_marzban_username",
        "users",
        ["marzban_username"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_users_marzban_username", table_name="users")
    op.drop_column("users", "marzban_username")
