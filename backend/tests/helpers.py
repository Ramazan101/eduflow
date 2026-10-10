from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.administrator import Administrator
from app.schemas.institution import InstitutionCreate
from app.schemas.program import ProgramCreate
from app.schemas.requirement_profile import (
    RequirementProfileCreate,
    RequirementProfileVerify,
)
from app.services.auth import AuthService
from app.services.catalog import CatalogService

TEST_ADMIN_EMAIL = "registrar@example.edu"
TEST_ADMIN_PASSWORD = "synthetic-admin-pass-12"


async def seed_verified_catalog(session: AsyncSession):
    catalog = CatalogService(session)
    suffix = uuid4().hex[:8]
    institution = await catalog.create_institution(
        InstitutionCreate(name="Northstar Academy", slug=f"northstar-{suffix}")
    )
    program = await catalog.create_program(
        ProgramCreate(institution_id=institution.id, name="Computer Science")
    )
    profile = await catalog.create_requirement_profile(
        RequirementProfileCreate(
            institution_id=institution.id,
            name="Undergraduate 2026",
            source_reference="https://example.edu/admissions/ug-2026",
        )
    )
    profile = await catalog.verify_requirement_profile(
        profile.id,
        RequirementProfileVerify(approval_reference="REG-MINUTES-2026-01"),
    )
    return institution, program, profile


async def seed_admin(session: AsyncSession) -> Administrator:
    return await AuthService(session).create(TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
