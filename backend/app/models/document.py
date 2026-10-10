import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import DocumentType

if TYPE_CHECKING:
    from app.models.application import Application


class Document(Base):
    __tablename__ = "documents"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    doc_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type", native_enum=True),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    application: Mapped["Application"] = relationship(back_populates="documents")
