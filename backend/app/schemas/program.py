import uuid

from pydantic import Field

from app.schemas.common import StrictModel, TimestampedResponse


class ProgramCreate(StrictModel):
    institution_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    is_active: bool = True


class ProgramResponse(TimestampedResponse):
    institution_id: uuid.UUID
    name: str
    is_active: bool
