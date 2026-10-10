from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.application import ApplicationRepository
from app.services.exceptions import DocumentNotFoundError


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._applications = ApplicationRepository(session)

    async def create(self, data: DocumentCreate) -> Document:
        await self._applications.get_by_id_or_raise(data.application_id)
        document = Document(**data.model_dump())
        self._session.add(document)
        await self._session.commit()
        await self._session.refresh(document)
        return document

    async def get_by_id(self, document_id: UUID) -> Document | None:
        result = await self._session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, document_id: UUID) -> Document:
        document = await self.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        return document

    async def list_by_application(self, application_id: UUID) -> list[Document]:
        await self._applications.get_by_id_or_raise(application_id)
        result = await self._session.execute(
            select(Document)
            .where(Document.application_id == application_id)
            .order_by(Document.created_at.asc())
        )
        return list(result.scalars().all())

    async def update(self, document_id: UUID, data: DocumentUpdate) -> Document:
        document = await self.get_by_id_or_raise(document_id)
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(document, field, value)
        await self._session.commit()
        await self._session.refresh(document)
        return document

    async def delete(self, document_id: UUID) -> None:
        document = await self.get_by_id_or_raise(document_id)
        await self._session.delete(document)
        await self._session.commit()
