from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.enums import ApplicationStatus, RequirementVerificationStatus
from app.models.requirement_profile import RequirementProfile
from app.schemas.application import ApplicationCreate
from app.schemas.institution import InstitutionCreate
from app.schemas.program import ProgramCreate
from app.schemas.requirement_profile import (
    RequirementProfileCreate,
    RequirementProfileVerify,
)
from app.services.application import ApplicationService
from app.services.catalog import CatalogService
from app.services.exceptions import (
    InvalidTransitionError,
    RequirementError,
)
from tests.helpers import seed_admin, seed_verified_catalog

pytestmark = pytest.mark.usefixtures("truncate_tables")


def _application_payload(program_id, profile_id, email: str) -> ApplicationCreate:
    return ApplicationCreate(
        program_id=program_id,
        requirement_profile_id=profile_id,
        applicant_name="Amina Karimova",
        birth_date=date(2004, 3, 12),
        phone="+77011234567",
        email=email,
    )


@pytest.mark.asyncio
async def test_create_application_writes_status_history(
    db_session: AsyncSession,
) -> None:
    _, program, profile = await seed_verified_catalog(db_session)
    service = ApplicationService(db_session)
    application = await service.create(
        _application_payload(program.id, profile.id, "amina@example.edu")
    )
    assert application.status == ApplicationStatus.NEW
    assert len(application.status_history) == 1
    assert application.status_history[0].from_status is None
    assert application.status_history[0].to_status == ApplicationStatus.NEW


@pytest.mark.asyncio
async def test_phone_is_not_globally_unique(db_session: AsyncSession) -> None:
    _, program, profile = await seed_verified_catalog(db_session)
    service = ApplicationService(db_session)
    first = await service.create(
        _application_payload(program.id, profile.id, "amina@example.edu")
    )
    second = await service.create(
        _application_payload(program.id, profile.id, "bekzat@example.edu")
    )
    assert first.phone == second.phone
    assert first.id != second.id


@pytest.mark.asyncio
async def test_unverified_profile_cannot_be_used(db_session: AsyncSession) -> None:
    catalog = CatalogService(db_session)
    institution = await catalog.create_institution(
        InstitutionCreate(name="Northstar Academy", slug=f"ns-{uuid4().hex[:8]}")
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
    service = ApplicationService(db_session)
    with pytest.raises(RequirementError, match="verified"):
        await service.create(
            _application_payload(program.id, profile.id, "amina@example.edu")
        )


@pytest.mark.asyncio
async def test_profile_must_match_program_institution(db_session: AsyncSession) -> None:
    _, program, _ = await seed_verified_catalog(db_session)
    other_institution, _, other_profile = await seed_verified_catalog(db_session)
    assert program.institution_id != other_institution.id
    service = ApplicationService(db_session)
    with pytest.raises(RequirementError, match="same institution"):
        await service.create(
            _application_payload(program.id, other_profile.id, "amina@example.edu")
        )


@pytest.mark.asyncio
async def test_status_transitions_and_history(db_session: AsyncSession) -> None:
    _, program, profile = await seed_verified_catalog(db_session)
    service = ApplicationService(db_session)
    application = await service.create(
        _application_payload(program.id, profile.id, "amina@example.edu")
    )
    with pytest.raises(InvalidTransitionError):
        await service.change_status(application.id, ApplicationStatus.ACCEPTED)

    admin = await seed_admin(db_session)
    pending = await service.change_status(
        application.id,
        ApplicationStatus.PENDING_REVIEW,
        note="Ready for registrar review",
        actor=admin,
    )
    assert pending.status == ApplicationStatus.PENDING_REVIEW
    accepted = await service.change_status(
        pending.id,
        ApplicationStatus.ACCEPTED,
        note="Offer issued",
        actor=admin,
    )
    assert accepted.status == ApplicationStatus.ACCEPTED
    assert [row.to_status for row in accepted.status_history] == [
        ApplicationStatus.NEW,
        ApplicationStatus.PENDING_REVIEW,
        ApplicationStatus.ACCEPTED,
    ]
    assert accepted.status_history[0].changed_by_id is None
    assert accepted.status_history[1].changed_by_id == admin.id
    assert accepted.status_history[2].changed_by_id == admin.id
    with pytest.raises(InvalidTransitionError):
        await service.change_status(accepted.id, ApplicationStatus.REJECTED)


@pytest.mark.asyncio
async def test_retired_profile_cannot_be_verified(db_session: AsyncSession) -> None:
    catalog = CatalogService(db_session)
    institution = await catalog.create_institution(
        InstitutionCreate(name="Northstar Academy", slug=f"ns-{uuid4().hex[:8]}")
    )
    profile = await catalog.create_requirement_profile(
        RequirementProfileCreate(
            institution_id=institution.id,
            name="Undergraduate 2025",
            source_reference="https://example.edu/admissions/ug-2025",
        )
    )
    stored = await db_session.get(RequirementProfile, profile.id)
    assert stored is not None
    stored.verification_status = RequirementVerificationStatus.RETIRED
    await db_session.commit()

    with pytest.raises(RequirementError, match="Retired"):
        await catalog.verify_requirement_profile(
            profile.id,
            RequirementProfileVerify(approval_reference="REG-MINUTES-2025-09"),
        )


@pytest.mark.asyncio
async def test_create_does_not_insert_on_validation_failure(
    db_session: AsyncSession,
) -> None:
    catalog = CatalogService(db_session)
    institution = await catalog.create_institution(
        InstitutionCreate(name="Northstar Academy", slug=f"ns-{uuid4().hex[:8]}")
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
    service = ApplicationService(db_session)
    with pytest.raises(RequirementError):
        await service.create(
            _application_payload(program.id, profile.id, "amina@example.edu")
        )
    result = await db_session.execute(select(Application))
    assert result.scalars().all() == []
