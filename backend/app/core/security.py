from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings

_hasher = PasswordHasher()
_TIMING_DUMMY_HASH = _hasher.hash("eduflow-unused-timing-dummy")

JWT_ALGORITHM = "HS256"
JWT_TOKEN_TYPE = "access"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed_password: str | None) -> bool:
    """Verify a password. Uses a dummy hash when the account is missing."""
    target = hashed_password or _TIMING_DUMMY_HASH
    try:
        return _hasher.verify(target, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(*, subject: UUID, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    lifetime = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "typ": JWT_TOKEN_TYPE,
        "iat": now,
        "exp": now + lifetime,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "sub", "typ"]},
        )
    except InvalidTokenError as exc:
        raise ValueError("Invalid access token") from exc
    if payload.get("typ") != JWT_TOKEN_TYPE:
        raise ValueError("Invalid access token")
    try:
        return UUID(str(payload["sub"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid access token") from exc
