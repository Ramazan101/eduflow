from fastapi import APIRouter

from app.api.v1.applications import router as applications_router

api_router = APIRouter()
api_router.include_router(
    applications_router,
    prefix="/applications",
    tags=["applications"],
)
