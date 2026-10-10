from pydantic import EmailStr, Field

from app.models.enums import UserRole
from app.schemas.common import StrictModel, TimestampedResponse


class UserCreate(StrictModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.ADMIN


class UserUpdate(StrictModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: UserRole | None = None


class UserResponse(TimestampedResponse):
    email: EmailStr
    role: UserRole
