"""Initial schema for institutions, programs, requirement profiles, and applications.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

application_status = postgresql.ENUM(
    "NEW",
    "PENDING_REVIEW",
    "ACCEPTED",
    "REJECTED",
    name="application_status",
    create_type=False,
)
requirement_verification_status = postgresql.ENUM(
    "UNVERIFIED",
    "VERIFIED",
    "RETIRED",
    name="requirement_verification_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute(
        "CREATE TYPE application_status AS ENUM "
        "('NEW', 'PENDING_REVIEW', 'ACCEPTED', 'REJECTED')"
    )
    op.execute(
        "CREATE TYPE requirement_verification_status AS ENUM "
        "('UNVERIFIED', 'VERIFIED', 'RETIRED')"
    )

    op.create_table(
        "institutions",
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
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "programs",
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
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(
            ["institution_id"],
            ["institutions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_programs_institution_id"),
        "programs",
        ["institution_id"],
        unique=False,
    )

    op.create_table(
        "requirement_profiles",
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
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_reference", sa.String(length=512), nullable=False),
        sa.Column("approval_reference", sa.String(length=512), nullable=True),
        sa.Column(
            "verification_status",
            requirement_verification_status,
            nullable=False,
            server_default="UNVERIFIED",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["institution_id"],
            ["institutions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_requirement_profiles_institution_id"),
        "requirement_profiles",
        ["institution_id"],
        unique=False,
    )

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
        sa.Column("program_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_profile_id", sa.Uuid(), nullable=False),
        sa.Column("applicant_name", sa.String(length=255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("phone", sa.String(length=16), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("status", application_status, nullable=False, server_default="NEW"),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["program_id"],
            ["programs.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requirement_profile_id"],
            ["requirement_profiles.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_applications_program_id"),
        "applications",
        ["program_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_applications_requirement_profile_id"),
        "applications",
        ["requirement_profile_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_applications_phone"),
        "applications",
        ["phone"],
        unique=False,
    )
    op.create_index(
        op.f("ix_applications_email"),
        "applications",
        ["email"],
        unique=False,
    )

    op.create_table(
        "application_status_history",
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
        sa.Column("from_status", application_status, nullable=True),
        sa.Column("to_status", application_status, nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_application_status_history_application_id"),
        "application_status_history",
        ["application_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_application_status_history_application_id"),
        table_name="application_status_history",
    )
    op.drop_table("application_status_history")
    op.drop_index(op.f("ix_applications_email"), table_name="applications")
    op.drop_index(op.f("ix_applications_phone"), table_name="applications")
    op.drop_index(
        op.f("ix_applications_requirement_profile_id"),
        table_name="applications",
    )
    op.drop_index(op.f("ix_applications_program_id"), table_name="applications")
    op.drop_table("applications")
    op.drop_index(
        op.f("ix_requirement_profiles_institution_id"),
        table_name="requirement_profiles",
    )
    op.drop_table("requirement_profiles")
    op.drop_index(op.f("ix_programs_institution_id"), table_name="programs")
    op.drop_table("programs")
    op.drop_table("institutions")
    op.execute("DROP TYPE IF EXISTS requirement_verification_status")
    op.execute("DROP TYPE IF EXISTS application_status")
