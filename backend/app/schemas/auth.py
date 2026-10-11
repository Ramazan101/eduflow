from pydantic import EmailStr, Field

from app.schemas.common import StrictModel


class LoginRequest(StrictModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class TokenResponse(StrictModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
