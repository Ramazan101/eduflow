from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DBSession
from app.models.enums import ApplicationStatus
from app.schemas.application import (
    ApplicationCreate,
    ApplicationCreatedResponse,
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatusUpdate,
)
from app.services.application import ApplicationRepository
from app.services.exceptions import (
    ApplicationNotFoundError,
    DuplicatePhoneError,
    PdfGenerationError,
)
from app.services.pdf_service import delete_generated_file, generate_contract_pdf

router = APIRouter()


@router.post(
    "/",
    response_model=ApplicationCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an application",
)
async def create_application(
    payload: ApplicationCreate,
    db: DBSession,
) -> ApplicationCreatedResponse:
    repository = ApplicationRepository(db)
    try:
        application = await repository.create(payload)
    except DuplicatePhoneError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An application with this phone number already exists.",
        ) from exc
    return ApplicationCreatedResponse(id=application.id)


@router.get(
    "/",
    response_model=ApplicationListResponse,
    summary="List applications",
)
async def list_applications(
    db: DBSession,
    status_filter: Annotated[
        ApplicationStatus | None,
        Query(alias="status", description="Filter by application status"),
    ] = None,
    course_name: Annotated[
        str | None,
        Query(min_length=1, description="Filter by course name (partial match)"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ApplicationListResponse:
    repository = ApplicationRepository(db)
    items, total = await repository.list(
        status=status_filter,
        course_name=course_name,
        limit=limit,
        offset=offset,
    )
    return ApplicationListResponse(
        items=[ApplicationResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{application_id}",
    response_model=ApplicationDetailResponse,
    summary="Get application details",
)
async def get_application(
    application_id: UUID,
    db: DBSession,
) -> ApplicationDetailResponse:
    repository = ApplicationRepository(db)
    try:
        application = await repository.get_by_id_or_raise(
            application_id,
            with_documents=True,
        )
    except ApplicationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        ) from exc
    return ApplicationDetailResponse.model_validate(application)


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    summary="Update application status",
)
async def update_application_status(
    application_id: UUID,
    payload: ApplicationStatusUpdate,
    db: DBSession,
) -> ApplicationResponse:
    repository = ApplicationRepository(db)
    try:
        application = await repository.update_status(application_id, payload)
    except ApplicationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        ) from exc
    return ApplicationResponse.model_validate(application)


@router.post(
    "/{application_id}/generate-contract",
    response_model=ApplicationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a training contract PDF",
)
async def generate_application_contract(
    application_id: UUID,
    db: DBSession,
) -> ApplicationDetailResponse:
    repository = ApplicationRepository(db)
    file_path: str | None = None
    try:
        application = await repository.get_by_id_or_raise(application_id)
        file_path = await generate_contract_pdf(application)
        application = await repository.attach_generated_contract(
            application,
            file_path,
        )
    except ApplicationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        ) from exc
    except PdfGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate the contract PDF.",
        ) from exc
    except Exception as exc:
        if file_path is not None:
            delete_generated_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the generated contract.",
        ) from exc
    return ApplicationDetailResponse.model_validate(application)
