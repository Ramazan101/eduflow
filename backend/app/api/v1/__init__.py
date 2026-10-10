from fastapi import APIRouter

from app.api.v1 import applications, auth, catalog, documents

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    applications.router,
    prefix="/applications",
    tags=["applications"],
)
api_router.include_router(
    documents.router,
    prefix="/applications",
    tags=["documents"],
)
api_router.include_router(catalog.router, tags=["catalog"])
