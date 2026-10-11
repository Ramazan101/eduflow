"""Add administrators and record who changed application status.

Revision ID: 0002_admins
Revises: 0001_initial
Create Date: 2026-10-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_admins"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "administrators",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(
        op.f("ix_administrators_email"),
        "administrators",
        ["email"],
        unique=True,
    )
    op.add_column(
        "application_status_history",
        sa.Column("changed_by_id", sa.Uuid(), nullable=True),
    )
    op.create_index(
        op.f("ix_application_status_history_changed_by_id"),
        "application_status_history",
        ["changed_by_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_status_history_changed_by_id",
        "application_status_history",
        "administrators",
        ["changed_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_status_history_changed_by_id",
        "application_status_history",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_application_status_history_changed_by_id"),
        table_name="application_status_history",
    )
    op.drop_column("application_status_history", "changed_by_id")
    op.drop_index(op.f("ix_administrators_email"), table_name="administrators")
    op.drop_table("administrators")
