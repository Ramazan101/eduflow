import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ApplicationStatus

if TYPE_CHECKING:
    from app.models.document import GeneratedDocument
    from app.models.program import Program
    from app.models.requirement_profile import RequirementProfile
    from app.models.status_history import ApplicationStatusHistory


class Application(Base):
    __tablename__ = "applications"

    program_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("programs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    requirement_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirement_profiles.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    applicant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", native_enum=True),
        default=ApplicationStatus.NEW,
        nullable=False,
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    program: Mapped["Program"] = relationship(back_populates="applications")
    requirement_profile: Mapped["RequirementProfile"] = relationship(
        back_populates="applications",
    )
    status_history: Mapped[list["ApplicationStatusHistory"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationStatusHistory.created_at, ApplicationStatusHistory.id",
    )
    documents: Mapped[list["GeneratedDocument"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="GeneratedDocument.created_at",
    )
