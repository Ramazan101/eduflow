import uuid

from pydantic import Field

from app.models.enums import DocumentType
from app.schemas.common import StrictModel, TimestampedResponse


class DocumentCreate(StrictModel):
    application_id: uuid.UUID
    doc_type: DocumentType
    file_path: str = Field(min_length=1, max_length=1024)


class DocumentUpdate(StrictModel):
    doc_type: DocumentType | None = None
    file_path: str | None = Field(default=None, min_length=1, max_length=1024)


class DocumentResponse(TimestampedResponse):
    application_id: uuid.UUID
    doc_type: DocumentType
    file_path: str
