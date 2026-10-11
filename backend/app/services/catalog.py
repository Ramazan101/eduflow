from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RequirementVerificationStatus
from app.models.institution import Institution
from app.models.program import Program
from app.models.requirement_profile import RequirementProfile
from app.schemas.institution import InstitutionCreate
from app.schemas.program import ProgramCreate
from app.schemas.requirement_profile import (
    RequirementProfileCreate,
    RequirementProfileVerify,
)
from app.services.exceptions import (
    InstitutionNotFoundError,
    ProgramNotFoundError,
    RequirementError,
    RequirementProfileNotFoundError,
)


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_institution(self, data: InstitutionCreate) -> Institution:
        institution = Institution(name=data.name, slug=data.slug)
        self._session.add(institution)
        await self._session.commit()
        await self._session.refresh(institution)
        return institution

    async def list_institutions(self) -> list[Institution]:
        result = await self._session.execute(
            select(Institution).order_by(Institution.name)
        )
        return list(result.scalars().all())

    async def get_institution(self, institution_id: UUID) -> Institution:
        result = await self._session.execute(
            select(Institution).where(Institution.id == institution_id)
        )
        institution = result.scalar_one_or_none()
        if institution is None:
            raise InstitutionNotFoundError(institution_id)
        return institution

    async def create_program(self, data: ProgramCreate) -> Program:
        await self.get_institution(data.institution_id)
        program = Program(
            institution_id=data.institution_id,
            name=data.name,
            is_active=data.is_active,
        )
        self._session.add(program)
        await self._session.commit()
        await self._session.refresh(program)
        return program

    async def list_programs(
        self,
        *,
        institution_id: UUID | None = None,
        active_only: bool = True,
    ) -> list[Program]:
        stmt = select(Program).order_by(Program.name)
        if institution_id is not None:
            stmt = stmt.where(Program.institution_id == institution_id)
        if active_only:
            stmt = stmt.where(Program.is_active.is_(True))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_program(self, program_id: UUID) -> Program:
        result = await self._session.execute(
            select(Program).where(Program.id == program_id)
        )
        program = result.scalar_one_or_none()
        if program is None:
            raise ProgramNotFoundError(program_id)
        return program

    async def create_requirement_profile(
        self,
        data: RequirementProfileCreate,
    ) -> RequirementProfile:
        await self.get_institution(data.institution_id)
        profile = RequirementProfile(
            institution_id=data.institution_id,
            name=data.name,
            source_reference=data.source_reference,
            approval_reference=data.approval_reference,
            verification_status=RequirementVerificationStatus.UNVERIFIED,
            notes=data.notes,
        )
        self._session.add(profile)
        await self._session.commit()
        await self._session.refresh(profile)
        return profile

    async def list_requirement_profiles(
        self,
        *,
        institution_id: UUID | None = None,
        verified_only: bool = True,
    ) -> list[RequirementProfile]:
        stmt = select(RequirementProfile).order_by(RequirementProfile.name)
        if institution_id is not None:
            stmt = stmt.where(RequirementProfile.institution_id == institution_id)
        if verified_only:
            stmt = stmt.where(
                RequirementProfile.verification_status
                == RequirementVerificationStatus.VERIFIED
            )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_requirement_profile(self, profile_id: UUID) -> RequirementProfile:
        result = await self._session.execute(
            select(RequirementProfile).where(RequirementProfile.id == profile_id)
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            raise RequirementProfileNotFoundError(profile_id)
        return profile

    async def verify_requirement_profile(
        self,
        profile_id: UUID,
        data: RequirementProfileVerify,
    ) -> RequirementProfile:
        profile = await self.get_requirement_profile(profile_id)
        if profile.verification_status == RequirementVerificationStatus.RETIRED:
            raise RequirementError("Retired requirement profiles cannot be verified")
        profile.approval_reference = data.approval_reference
        profile.verification_status = RequirementVerificationStatus.VERIFIED
        await self._session.commit()
        await self._session.refresh(profile)
        return profile
