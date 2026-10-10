"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = sa.Enum("ADMIN", name="user_role")
application_status = sa.Enum(
    "NEW",
    "PENDING_REVIEW",
    "CONTRACT_GENERATED",
    "ACCEPTED",
    "REJECTED",
    name="application_status",
)
document_type = sa.Enum("QUESTIONNAIRE", "CONTRACT", name="document_type")


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    application_status.create(op.get_bind(), checkfirst=True)
    document_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
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
        sa.Column("role", user_role, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "applications",
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
        sa.Column("applicant_name", sa.String(length=255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("phone", sa.String(length=16), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("course_name", sa.String(length=255), nullable=False),
        sa.Column("status", application_status, nullable=False),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
    )
    op.create_index(
        op.f("ix_applications_phone"),
        "applications",
        ["phone"],
        unique=True,
    )
    op.create_index(
        op.f("ix_applications_email"),
        "applications",
        ["email"],
        unique=False,
    )

    op.create_table(
        "documents",
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
        sa.Column("doc_type", document_type, nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_documents_application_id"),
        "documents",
        ["application_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_documents_application_id"), table_name="documents")
    op.drop_table("documents")
    op.drop_index(op.f("ix_applications_email"), table_name="applications")
    op.drop_index(op.f("ix_applications_phone"), table_name="applications")
    op.drop_table("applications")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    document_type.drop(op.get_bind(), checkfirst=True)
    application_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
