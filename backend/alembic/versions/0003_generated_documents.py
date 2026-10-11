"""Store generated document metadata without filesystem paths in the API.

Revision ID: 0003_documents
Revises: 0002_admins
Create Date: 2026-10-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_documents"
down_revision: Union[str, Sequence[str], None] = "0002_admins"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE document_generation_status AS ENUM ('SUCCESS', 'FAILED')"
    )
    op.create_table(
        "generated_documents",
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
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("template_key", sa.String(length=64), nullable=False),
        sa.Column("template_version", sa.String(length=32), nullable=False),
        sa.Column(
            "generation_status",
            postgresql.ENUM(
                "SUCCESS",
                "FAILED",
                name="document_generation_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("storage_key", sa.String(length=64), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("generated_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["generated_by_id"],
            ["administrators.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_generated_documents_application_id"),
        "generated_documents",
        ["application_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_documents_generated_by_id"),
        "generated_documents",
        ["generated_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_generated_documents_generated_by_id"),
        table_name="generated_documents",
    )
    op.drop_index(
        op.f("ix_generated_documents_application_id"),
        table_name="generated_documents",
    )
    op.drop_table("generated_documents")
    op.execute("DROP TYPE IF EXISTS document_generation_status")
