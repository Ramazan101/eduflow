import uuid

from app.models.enums import DocumentGenerationStatus
from app.schemas.common import TimestampedResponse


class DocumentMetadataResponse(TimestampedResponse):
    application_id: uuid.UUID
    template_key: str
    template_version: str
    generation_status: DocumentGenerationStatus
    error_code: str | None
