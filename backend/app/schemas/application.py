import uuid
from datetime import date

from pydantic import EmailStr, Field, field_validator

from app.models.enums import ApplicationStatus
from app.schemas.common import ORMModel, PhoneNumber, StrictModel, TimestampedResponse


class ApplicationCreate(StrictModel):
    program_id: uuid.UUID
    requirement_profile_id: uuid.UUID
    applicant_name: str = Field(min_length=1, max_length=255)
    birth_date: date
    phone: PhoneNumber
    email: EmailStr

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("birth_date cannot be in the future")
        return value


class ApplicationStatusChange(StrictModel):
    status: ApplicationStatus
    note: str | None = Field(default=None, max_length=2000)


class ApplicationCreatedResponse(StrictModel):
    id: uuid.UUID
    status: ApplicationStatus


class StatusHistoryResponse(TimestampedResponse):
    application_id: uuid.UUID
    from_status: ApplicationStatus | None
    to_status: ApplicationStatus
    note: str | None
    changed_by_id: uuid.UUID | None


class ApplicationStatusResponse(ORMModel):
    id: uuid.UUID
    status: ApplicationStatus
    status_history: list[StatusHistoryResponse] = Field(default_factory=list)


class ApplicationListItem(TimestampedResponse):
    program_id: uuid.UUID
    requirement_profile_id: uuid.UUID
    applicant_name: str
    birth_date: date
    phone: PhoneNumber
    email: EmailStr
    status: ApplicationStatus


class ApplicationListResponse(StrictModel):
    items: list[ApplicationListItem]
    total: int
    limit: int
    offset: int


class ApplicationResponse(TimestampedResponse):
    program_id: uuid.UUID
    requirement_profile_id: uuid.UUID
    applicant_name: str
    birth_date: date
    phone: PhoneNumber
    email: EmailStr
    status: ApplicationStatus
    admin_notes: str | None
    status_history: list[StatusHistoryResponse] = Field(default_factory=list)
