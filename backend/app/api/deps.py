from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.administrator import Administrator
from app.services.auth import AuthService
from app.services.exceptions import AuthenticationError

DBSession = Annotated[AsyncSession, Depends(get_db)]
_bearer = HTTPBearer(auto_error=False)


async def get_current_admin(
    db: DBSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer),
    ],
) -> Administrator:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Not authenticated")
    return await AuthService(db).require_active_from_token(credentials.credentials)


CurrentAdmin = Annotated[Administrator, Depends(get_current_admin)]
