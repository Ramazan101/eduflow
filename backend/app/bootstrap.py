"""Create the first administrator from environment variables.

This command never runs automatically on application startup.
It refuses to run in production unless EDUFLOW_ALLOW_ADMIN_BOOTSTRAP=true.
It does not insert a built-in password.
"""

from __future__ import annotations

import asyncio
import os
import sys

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.services.auth import AuthService

MIN_PASSWORD_LENGTH = 12


async def bootstrap_admin() -> int:
    settings = get_settings()
    if settings.environment.lower() == "production" and not settings.allow_admin_bootstrap:
        print(
            "Refusing to bootstrap an administrator in production. "
            "Set EDUFLOW_ALLOW_ADMIN_BOOTSTRAP=true only for a controlled setup.",
            file=sys.stderr,
        )
        return 1

    email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "").strip()
    password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "")
    if not email or not password:
        print(
            "Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD in the environment. "
            "Do not commit those values.",
            file=sys.stderr,
        )
        return 1
    if len(password) < MIN_PASSWORD_LENGTH:
        print(
            f"BOOTSTRAP_ADMIN_PASSWORD must be at least {MIN_PASSWORD_LENGTH} characters.",
            file=sys.stderr,
        )
        return 1

    async with AsyncSessionLocal() as session:
        service = AuthService(session)
        if await service.count() > 0:
            print("An administrator already exists. No account was created.")
            return 0
        administrator = await service.create(email, password)

    print(f"Created administrator {administrator.email} ({administrator.id}).")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(bootstrap_admin()))


if __name__ == "__main__":
    main()
