import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ApplicationStatus

if TYPE_CHECKING:
    from app.models.administrator import Administrator
    from app.models.application import Application


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("administrators.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    from_status: Mapped[ApplicationStatus | None] = mapped_column(
        Enum(
            ApplicationStatus,
            name="application_status",
            native_enum=True,
            create_constraint=False,
        ),
        nullable=True,
    )
    to_status: Mapped[ApplicationStatus] = mapped_column(
        Enum(
            ApplicationStatus,
            name="application_status",
            native_enum=True,
            create_constraint=False,
        ),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    application: Mapped["Application"] = relationship(back_populates="status_history")
    changed_by: Mapped["Administrator | None"] = relationship()
