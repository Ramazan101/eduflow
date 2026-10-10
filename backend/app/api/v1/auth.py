from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.core.config import get_settings
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: DBSession) -> TokenResponse:
    administrator = await AuthService(db).authenticate(payload.email, payload.password)
    token = AuthService.issue_token(administrator)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=get_settings().access_token_expire_minutes * 60,
    )
