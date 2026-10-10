import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.health import health
from main import app


@pytest.mark.asyncio
async def test_health_reports_database_without_secrets() -> None:
    response = await health()
    body = json.loads(response.body)
    assert set(body.keys()) == {"status", "database"}
    assert body["database"] in {"connected", "disconnected"}
    blob = response.body.decode().lower()
    assert "password" not in blob
    assert "database_url" not in blob
    assert "postgresql+" not in blob


@pytest.mark.asyncio
async def test_health_ok_when_database_is_reachable() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
