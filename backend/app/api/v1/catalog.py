from uuid import UUID

from fastapi import APIRouter

from app.api.deps import DBSession
from app.schemas.institution import InstitutionResponse
from app.schemas.program import ProgramResponse
from app.schemas.requirement_profile import RequirementProfilePublicResponse
from app.services.catalog import CatalogService

router = APIRouter()


@router.get("/institutions", response_model=list[InstitutionResponse])
async def list_institutions(db: DBSession) -> list[InstitutionResponse]:
    institutions = await CatalogService(db).list_institutions()
    return [InstitutionResponse.model_validate(item) for item in institutions]


@router.get("/programs", response_model=list[ProgramResponse])
async def list_programs(
    db: DBSession,
    institution_id: UUID | None = None,
) -> list[ProgramResponse]:
    programs = await CatalogService(db).list_programs(
        institution_id=institution_id,
        active_only=True,
    )
    return [ProgramResponse.model_validate(item) for item in programs]


@router.get(
    "/requirement-profiles",
    response_model=list[RequirementProfilePublicResponse],
)
async def list_requirement_profiles(
    db: DBSession,
    institution_id: UUID | None = None,
) -> list[RequirementProfilePublicResponse]:
    profiles = await CatalogService(db).list_requirement_profiles(
        institution_id=institution_id,
        verified_only=True,
    )
    return [
        RequirementProfilePublicResponse.model_validate(item) for item in profiles
    ]
