import os
from collections.abc import AsyncIterator

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://eduflow:eduflow@127.0.0.1:5432/eduflow",
)
os.environ.setdefault(
    "SECRET_KEY",
    "eduflow-test-secret-key-not-for-production-use",
)

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, engine
from main import app

get_settings.cache_clear()


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def truncate_tables() -> AsyncIterator[None]:
    yield
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE generated_documents, application_status_history, "
                "applications, requirement_profiles, programs, institutions, "
                "administrators CASCADE"
            )
        )


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as instance:
        yield instance
