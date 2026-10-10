import uuid

from pydantic import Field

from app.models.enums import RequirementVerificationStatus
from app.schemas.common import StrictModel, TimestampedResponse


class RequirementProfileCreate(StrictModel):
    institution_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    source_reference: str = Field(min_length=1, max_length=512)
    approval_reference: str | None = Field(default=None, max_length=512)
    notes: str | None = None


class RequirementProfileVerify(StrictModel):
    approval_reference: str = Field(min_length=1, max_length=512)


class RequirementProfilePublicResponse(TimestampedResponse):
    institution_id: uuid.UUID
    name: str
    source_reference: str
    verification_status: RequirementVerificationStatus


class RequirementProfileResponse(TimestampedResponse):
    institution_id: uuid.UUID
    name: str
    source_reference: str
    approval_reference: str | None
    verification_status: RequirementVerificationStatus
    notes: str | None
