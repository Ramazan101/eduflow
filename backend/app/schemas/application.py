from datetime import date
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.models.enums import ApplicationStatus
from app.schemas.common import PhoneNumber, StrictModel, TimestampedResponse
from app.schemas.document import DocumentResponse


class ApplicationCreate(StrictModel):
    applicant_name: str = Field(min_length=1, max_length=255)
    birth_date: date
    phone: PhoneNumber
    email: EmailStr
    course_name: str = Field(min_length=1, max_length=255)

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("birth_date cannot be in the future")
        return value


class ApplicationUpdate(StrictModel):
    applicant_name: str | None = Field(default=None, min_length=1, max_length=255)
    birth_date: date | None = None
    phone: PhoneNumber | None = None
    email: EmailStr | None = None
    course_name: str | None = Field(default=None, min_length=1, max_length=255)
    status: ApplicationStatus | None = None
    admin_notes: str | None = None

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_in_future(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("birth_date cannot be in the future")
        return value


class ApplicationStatusUpdate(StrictModel):
    status: ApplicationStatus
    admin_notes: str | None = None


class ApplicationCreatedResponse(StrictModel):
    id: UUID


class ApplicationResponse(TimestampedResponse):
    applicant_name: str
    birth_date: date
    phone: PhoneNumber
    email: EmailStr
    course_name: str
    status: ApplicationStatus
    admin_notes: str | None


class ApplicationDetailResponse(ApplicationResponse):
    documents: list[DocumentResponse] = Field(default_factory=list)


class ApplicationListResponse(StrictModel):
    items: list[ApplicationResponse]
    total: int
    limit: int
    offset: int
