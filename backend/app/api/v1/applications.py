from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentAdmin, DBSession
from app.models.enums import ApplicationStatus
from app.schemas.application import (
    ApplicationCreatedResponse,
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatusChange,
    ApplicationStatusResponse,
)
from app.services.application import ApplicationService

router = APIRouter()


@router.post(
    "/",
    response_model=ApplicationCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_application(
    payload: ApplicationCreate,
    db: DBSession,
) -> ApplicationCreatedResponse:
    application = await ApplicationService(db).create(payload)
    return ApplicationCreatedResponse(id=application.id, status=application.status)


@router.get("/", response_model=ApplicationListResponse)
async def list_applications(
    db: DBSession,
    _admin: CurrentAdmin,
    status_filter: Annotated[ApplicationStatus | None, Query(alias="status")] = None,
    program_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ApplicationListResponse:
    items, total = await ApplicationService(db).list(
        status=status_filter,
        program_id=program_id,
        limit=limit,
        offset=offset,
    )
    return ApplicationListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    db: DBSession,
    _admin: CurrentAdmin,
) -> ApplicationResponse:
    application = await ApplicationService(db).get(application_id)
    return ApplicationResponse.model_validate(application)


@router.get("/{application_id}/status", response_model=ApplicationStatusResponse)
async def get_application_status(
    application_id: UUID,
    db: DBSession,
    _admin: CurrentAdmin,
) -> ApplicationStatusResponse:
    application = await ApplicationService(db).get(application_id)
    return ApplicationStatusResponse.model_validate(application)


@router.post("/{application_id}/status", response_model=ApplicationResponse)
async def change_application_status(
    application_id: UUID,
    payload: ApplicationStatusChange,
    db: DBSession,
    admin: CurrentAdmin,
) -> ApplicationResponse:
    application = await ApplicationService(db).change_status(
        application_id,
        payload.status,
        note=payload.note,
        actor=admin,
    )
    return ApplicationResponse.model_validate(application)
