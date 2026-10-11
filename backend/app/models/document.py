import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import DocumentGenerationStatus

if TYPE_CHECKING:
    from app.models.administrator import Administrator
    from app.models.application import Application


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    template_key: Mapped[str] = mapped_column(String(64), nullable=False)
    template_version: Mapped[str] = mapped_column(String(32), nullable=False)
    generation_status: Mapped[DocumentGenerationStatus] = mapped_column(
        Enum(
            DocumentGenerationStatus,
            name="document_generation_status",
            native_enum=True,
        ),
        nullable=False,
    )
    storage_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    generated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("administrators.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    application: Mapped["Application"] = relationship(back_populates="documents")
    generated_by: Mapped["Administrator | None"] = relationship()
