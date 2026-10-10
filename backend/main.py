from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.errors import register_error_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.project_name)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(application)
    application.include_router(health_router)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
