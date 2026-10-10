import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# E.164: '+' followed by 8–15 digits, first digit non-zero.
PHONE_NUMBER_PATTERN = r"^\+[1-9]\d{7,14}$"

PhoneNumber = Annotated[
    str,
    Field(
        pattern=PHONE_NUMBER_PATTERN,
        min_length=9,
        max_length=16,
        examples=["+77011234567"],
        description="E.164 phone number, e.g. +77011234567",
    ),
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ORMModel(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        from_attributes=True,
    )


class TimestampedResponse(ORMModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
