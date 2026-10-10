from pydantic import Field

from app.schemas.common import StrictModel, TimestampedResponse


class InstitutionCreate(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9-]+$")


class InstitutionResponse(TimestampedResponse):
    name: str
    slug: str
