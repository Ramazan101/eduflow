import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import RequirementVerificationStatus

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.institution import Institution


class RequirementProfile(Base):
    """Institution-approved admissions requirement set, not per-application data."""

    __tablename__ = "requirement_profiles"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_reference: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Catalog URL, policy ID, or other official source of the requirements.",
    )
    approval_reference: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="Internal approval record (minutes ID, ticket, or registrar reference).",
    )
    verification_status: Mapped[RequirementVerificationStatus] = mapped_column(
        Enum(
            RequirementVerificationStatus,
            name="requirement_verification_status",
            native_enum=True,
        ),
        default=RequirementVerificationStatus.UNVERIFIED,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    institution: Mapped["Institution"] = relationship(
        back_populates="requirement_profiles",
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="requirement_profile",
    )
