from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> JSONResponse:
    """Report process and database connectivity. Never includes secrets."""
    database_state = "disconnected"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        database_state = "connected"
        http_status = status.HTTP_200_OK
    except Exception:
        database_state = "disconnected"

    body = {
        "status": "ok" if database_state == "connected" else "unavailable",
        "database": database_state,
    }
    return JSONResponse(status_code=http_status, content=body)
