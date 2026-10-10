from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.administrator import Administrator
from app.models.application import Application
from app.models.enums import ApplicationStatus, RequirementVerificationStatus
from app.models.status_history import ApplicationStatusHistory
from app.schemas.application import ApplicationCreate
from app.services.catalog import CatalogService
from app.services.exceptions import (
    ApplicationNotFoundError,
    InvalidTransitionError,
    RequirementError,
)

ALLOWED_TRANSITIONS: dict[ApplicationStatus, frozenset[ApplicationStatus]] = {
    ApplicationStatus.NEW: frozenset(
        {ApplicationStatus.PENDING_REVIEW, ApplicationStatus.REJECTED}
    ),
    ApplicationStatus.PENDING_REVIEW: frozenset(
        {ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED}
    ),
    ApplicationStatus.ACCEPTED: frozenset(),
    ApplicationStatus.REJECTED: frozenset(),
}


class ApplicationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._catalog = CatalogService(session)

    async def create(self, data: ApplicationCreate) -> Application:
        program = await self._catalog.get_program(data.program_id)
        profile = await self._catalog.get_requirement_profile(
            data.requirement_profile_id
        )
        if program.institution_id != profile.institution_id:
            raise RequirementError(
                "Requirement profile must belong to the same institution as the program"
            )
        if profile.verification_status != RequirementVerificationStatus.VERIFIED:
            raise RequirementError(
                "Applications may only use a verified requirement profile"
            )

        application = Application(
            program_id=data.program_id,
            requirement_profile_id=data.requirement_profile_id,
            applicant_name=data.applicant_name,
            birth_date=data.birth_date,
            phone=data.phone,
            email=data.email,
            status=ApplicationStatus.NEW,
        )
        history = ApplicationStatusHistory(
            application=application,
            from_status=None,
            to_status=ApplicationStatus.NEW,
            note="Application submitted",
        )
        self._session.add(application)
        self._session.add(history)
        await self._session.commit()
        return await self.get(application.id)

    async def list(
        self,
        *,
        status: ApplicationStatus | None = None,
        program_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Application], int]:
        filters = []
        if status is not None:
            filters.append(Application.status == status)
        if program_id is not None:
            filters.append(Application.program_id == program_id)

        count_stmt = select(func.count()).select_from(Application)
        list_stmt = select(Application).order_by(Application.created_at.desc())
        if filters:
            count_stmt = count_stmt.where(*filters)
            list_stmt = list_stmt.where(*filters)
        total = int((await self._session.execute(count_stmt)).scalar_one())
        result = await self._session.execute(list_stmt.limit(limit).offset(offset))
        return list(result.scalars().all()), total

    async def get(self, application_id: UUID) -> Application:
        result = await self._session.execute(
            select(Application)
            .options(selectinload(Application.status_history))
            .where(Application.id == application_id)
            .execution_options(populate_existing=True)
        )
        application = result.scalar_one_or_none()
        if application is None:
            raise ApplicationNotFoundError(application_id)
        return application

    async def change_status(
        self,
        application_id: UUID,
        target: ApplicationStatus,
        note: str | None = None,
        actor: Administrator | None = None,
    ) -> Application:
        application = await self.get(application_id)
        allowed = ALLOWED_TRANSITIONS[application.status]
        if target not in allowed:
            raise InvalidTransitionError(application.status, target)

        history = ApplicationStatusHistory(
            application_id=application.id,
            from_status=application.status,
            to_status=target,
            note=note,
            changed_by_id=None if actor is None else actor.id,
        )
        application.status = target
        self._session.add(history)
        await self._session.commit()
        return await self.get(application_id)
