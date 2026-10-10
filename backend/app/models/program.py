import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.institution import Institution


class Program(Base):
    __tablename__ = "programs"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    institution: Mapped["Institution"] = relationship(back_populates="programs")
    applications: Mapped[list["Application"]] = relationship(back_populates="program")
