from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.document import Document
from app.models.enums import ApplicationStatus, DocumentType
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate
from app.services.exceptions import ApplicationNotFoundError, DuplicatePhoneError


class ApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ApplicationCreate) -> Application:
        application = Application(**data.model_dump())
        self._session.add(application)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if _is_phone_unique_violation(exc):
                raise DuplicatePhoneError(data.phone) from exc
            raise
        await self._session.refresh(application)
        return application

    async def get_by_id(
        self,
        application_id: UUID,
        *,
        with_documents: bool = False,
    ) -> Application | None:
        stmt: Select[tuple[Application]] = select(Application).where(
            Application.id == application_id
        )
        if with_documents:
            stmt = stmt.options(selectinload(Application.documents))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self,
        application_id: UUID,
        *,
        with_documents: bool = False,
    ) -> Application:
        application = await self.get_by_id(
            application_id,
            with_documents=with_documents,
        )
        if application is None:
            raise ApplicationNotFoundError(application_id)
        return application

    async def list(
        self,
        *,
        status: ApplicationStatus | None = None,
        course_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Application], int]:
        filters = []
        if status is not None:
            filters.append(Application.status == status)
        if course_name:
            filters.append(Application.course_name.ilike(f"%{course_name}%"))

        count_stmt = select(func.count()).select_from(Application)
        list_stmt: Select[tuple[Application]] = select(Application).order_by(
            Application.created_at.desc()
        )
        if filters:
            count_stmt = count_stmt.where(*filters)
            list_stmt = list_stmt.where(*filters)

        total = int((await self._session.execute(count_stmt)).scalar_one())
        result = await self._session.execute(list_stmt.limit(limit).offset(offset))
        return list(result.scalars().all()), total

    async def update_status(
        self,
        application_id: UUID,
        data: ApplicationStatusUpdate,
    ) -> Application:
        application = await self.get_by_id_or_raise(application_id)
        application.status = data.status
        if data.admin_notes is not None:
            application.admin_notes = data.admin_notes
        await self._session.commit()
        await self._session.refresh(application)
        return application

    async def attach_generated_contract(
        self,
        application: Application,
        file_path: str,
    ) -> Application:
        document = Document(
            application_id=application.id,
            doc_type=DocumentType.CONTRACT,
            file_path=file_path,
        )
        self._session.add(document)
        application.status = ApplicationStatus.CONTRACT_GENERATED
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise
        return await self.get_by_id_or_raise(
            application.id,
            with_documents=True,
        )


def _is_phone_unique_violation(exc: IntegrityError) -> bool:
    message = str(getattr(exc, "orig", exc)).lower()
    return "unique" in message and "phone" in message
