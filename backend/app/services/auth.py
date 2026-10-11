from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.administrator import Administrator
from app.services.exceptions import AuthenticationError, AuthorizationError

GENERIC_AUTH_FAILURE = "Invalid credentials"


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def authenticate(self, email: str, password: str) -> Administrator:
        normalized = email.strip().lower()
        result = await self._session.execute(
            select(Administrator).where(Administrator.email == normalized)
        )
        administrator = result.scalar_one_or_none()
        hashed = administrator.hashed_password if administrator is not None else None
        if not verify_password(password, hashed):
            raise AuthenticationError(GENERIC_AUTH_FAILURE)
        if administrator is None or not administrator.is_active:
            raise AuthenticationError(GENERIC_AUTH_FAILURE)
        return administrator

    async def get_by_id(self, administrator_id: UUID) -> Administrator | None:
        result = await self._session.execute(
            select(Administrator).where(Administrator.id == administrator_id)
        )
        return result.scalar_one_or_none()

    async def require_active_from_token(self, token: str) -> Administrator:
        try:
            administrator_id = decode_access_token(token)
        except ValueError as exc:
            raise AuthenticationError("Not authenticated") from exc
        administrator = await self.get_by_id(administrator_id)
        if administrator is None:
            raise AuthenticationError("Not authenticated")
        if not administrator.is_active:
            raise AuthorizationError("Not authorized")
        return administrator

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Administrator))
        return int(result.scalar_one())

    async def create(self, email: str, password: str) -> Administrator:
        administrator = Administrator(
            email=email.strip().lower(),
            hashed_password=hash_password(password),
            is_active=True,
        )
        self._session.add(administrator)
        await self._session.commit()
        await self._session.refresh(administrator)
        return administrator

    @staticmethod
    def issue_token(administrator: Administrator) -> str:
        return create_access_token(subject=administrator.id)
