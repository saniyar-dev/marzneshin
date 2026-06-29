"""add admin billing tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-28 14:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_billing",
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column(
            "total_billable_bytes",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("last_checkpoint_at", sa.DateTime(), nullable=True),
        sa.Column("last_checkpoint_bytes", sa.BigInteger(), nullable=True),
        sa.Column(
            "last_checkpoint_note", sa.String(length=512), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["admin_id"], ["admins.id"], name="fk_admin_billing_admin_id"
        ),
        sa.PrimaryKeyConstraint("admin_id"),
    )
    op.create_index(
        "ix_admin_billing_admin_id",
        "admin_billing",
        ["admin_id"],
        unique=False,
    )

    op.create_table(
        "admin_billing_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("bytes_amount", sa.BigInteger(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=True),
        sa.Column("note", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(
            ["admin_id"],
            ["admins.id"],
            name="fk_admin_billing_events_admin_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_admin_billing_events_user_id"
        ),
    )
    op.create_index(
        "ix_admin_billing_events_admin_id",
        "admin_billing_events",
        ["admin_id"],
        unique=False,
    )
    op.create_index(
        "ix_admin_billing_events_user_id",
        "admin_billing_events",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_admin_billing_events_occurred_at",
        "admin_billing_events",
        ["occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_admin_billing_events_occurred_at",
        table_name="admin_billing_events",
    )
    op.drop_index(
        "ix_admin_billing_events_user_id", table_name="admin_billing_events"
    )
    op.drop_index(
        "ix_admin_billing_events_admin_id", table_name="admin_billing_events"
    )
    op.drop_table("admin_billing_events")
    op.drop_index("ix_admin_billing_admin_id", table_name="admin_billing")
    op.drop_table("admin_billing")
