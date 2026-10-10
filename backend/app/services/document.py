from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from weasyprint import HTML

from app.core.storage import documents_root, resolve_storage_path
from app.models.administrator import Administrator
from app.models.application import Application
from app.models.document import GeneratedDocument
from app.models.enums import DocumentGenerationStatus
from app.models.program import Program
from app.services.application import ApplicationService
from app.services.exceptions import (
    ApplicationNotFoundError,
    DocumentNotFoundError,
    PdfGenerationError,
    TemplateDataError,
    TemplateUnavailableError,
    UnsafeStorageKeyError,
)

logger = logging.getLogger("eduflow.documents")

DEMO_DISCLAIMER = "DEMO — NOT A LEGAL DOCUMENT — NOT FOR SIGNING"
TEMPLATE_KEY = "demo_application_summary"
TEMPLATE_VERSION = "1.0.0"
TEMPLATE_FILENAME = "demo_application_summary_v1.html"
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

ERROR_MISSING_DATA = "MISSING_TEMPLATE_DATA"
ERROR_TEMPLATE_UNAVAILABLE = "TEMPLATE_UNAVAILABLE"
ERROR_RENDER_FAILED = "RENDER_FAILED"


class DocumentContext(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    disclaimer: str = Field(min_length=1)
    template_key: str = Field(min_length=1)
    template_version: str = Field(min_length=1)
    application_id: str = Field(min_length=1)
    applicant_name: str = Field(min_length=1, max_length=255)
    birth_date: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    email: str = Field(min_length=1)
    institution_name: str = Field(min_length=1)
    program_name: str = Field(min_length=1)
    requirement_profile_name: str = Field(min_length=1)
    application_status: str = Field(min_length=1)
    generated_at: str = Field(min_length=1)


def build_document_context(
    application: Application,
    *,
    generated_at: datetime | None = None,
) -> DocumentContext:
    program = application.program
    institution = program.institution if program is not None else None
    profile = application.requirement_profile
    payload = {
        "disclaimer": DEMO_DISCLAIMER,
        "template_key": TEMPLATE_KEY,
        "template_version": TEMPLATE_VERSION,
        "application_id": str(application.id) if application.id else "",
        "applicant_name": application.applicant_name or "",
        "birth_date": (
            application.birth_date.isoformat() if application.birth_date else ""
        ),
        "phone": application.phone or "",
        "email": application.email or "",
        "institution_name": institution.name if institution is not None else "",
        "program_name": program.name if program is not None else "",
        "requirement_profile_name": profile.name if profile is not None else "",
        "application_status": (
            application.status.value if application.status is not None else ""
        ),
        "generated_at": (generated_at or datetime.now(UTC)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
    }
    try:
        return DocumentContext.model_validate(payload)
    except ValidationError as exc:
        raise TemplateDataError("Required template data is missing") from exc


def _jinja_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_template_html(
    context: DocumentContext,
    *,
    templates_dir: Path | None = None,
    filename: str = TEMPLATE_FILENAME,
) -> str:
    directory = templates_dir or TEMPLATES_DIR
    env = _jinja_env(directory)
    try:
        template = env.get_template(filename)
    except TemplateNotFound as exc:
        raise TemplateUnavailableError() from exc
    return template.render(**context.model_dump())


def write_pdf(html: str, output_path: Path) -> None:
    HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf(target=str(output_path))


class DocumentService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        templates_dir: Path | None = None,
        template_filename: str = TEMPLATE_FILENAME,
        write_pdf_fn=write_pdf,
    ) -> None:
        self._session = session
        self._templates_dir = templates_dir or TEMPLATES_DIR
        self._template_filename = template_filename
        self._write_pdf = write_pdf_fn
        self._applications = ApplicationService(session)

    async def _load_application(self, application_id: UUID) -> Application:
        result = await self._session.execute(
            select(Application)
            .options(
                selectinload(Application.program).selectinload(Program.institution),
                selectinload(Application.requirement_profile),
            )
            .where(Application.id == application_id)
        )
        application = result.scalar_one_or_none()
        if application is None:
            raise ApplicationNotFoundError(application_id)
        return application

    async def _record_failure(
        self,
        application_id: UUID,
        error_code: str,
        actor_id: UUID | None,
    ) -> None:
        record = GeneratedDocument(
            application_id=application_id,
            template_key=TEMPLATE_KEY,
            template_version=TEMPLATE_VERSION,
            generation_status=DocumentGenerationStatus.FAILED,
            storage_key=None,
            error_code=error_code,
            generated_by_id=actor_id,
        )
        self._session.add(record)
        await self._session.commit()

    async def generate(
        self,
        application_id: UUID,
        actor: Administrator,
    ) -> GeneratedDocument:
        application = await self._load_application(application_id)
        status_before = application.status
        actor_id = actor.id
        document_id = uuid4()
        storage_key = f"{document_id}.pdf"
        output_path: Path | None = None

        try:
            context = build_document_context(application)
            html = render_template_html(
                context,
                templates_dir=self._templates_dir,
                filename=self._template_filename,
            )
            output_path = resolve_storage_path(documents_root(), storage_key)
            await asyncio.to_thread(self._write_pdf, html, output_path)
            if not output_path.is_file() or output_path.stat().st_size == 0:
                raise PdfGenerationError("Generated document is empty")
            record = GeneratedDocument(
                id=document_id,
                application_id=application.id,
                template_key=TEMPLATE_KEY,
                template_version=TEMPLATE_VERSION,
                generation_status=DocumentGenerationStatus.SUCCESS,
                storage_key=storage_key,
                error_code=None,
                generated_by_id=actor_id,
            )
            self._session.add(record)
            await self._session.commit()
        except TemplateDataError:
            if output_path is not None:
                output_path.unlink(missing_ok=True)
            await self._session.rollback()
            await self._record_failure(application_id, ERROR_MISSING_DATA, actor_id)
            raise
        except TemplateUnavailableError:
            if output_path is not None:
                output_path.unlink(missing_ok=True)
            await self._session.rollback()
            await self._record_failure(
                application_id, ERROR_TEMPLATE_UNAVAILABLE, actor_id
            )
            raise
        except ApplicationNotFoundError:
            raise
        except Exception:
            if output_path is not None:
                output_path.unlink(missing_ok=True)
            await self._session.rollback()
            await self._record_failure(application_id, ERROR_RENDER_FAILED, actor_id)
            logger.exception(
                "document_generation_failed application_id=%s",
                application_id,
            )
            raise PdfGenerationError() from None

        refreshed = await self._applications.get(application_id)
        if refreshed.status != status_before:
            logger.error(
                "document_generation_status_drift application_id=%s",
                application_id,
            )
            raise PdfGenerationError("Application status changed during generation")

        logger.info(
            "document_generated document_id=%s application_id=%s template=%s version=%s",
            record.id,
            application_id,
            TEMPLATE_KEY,
            TEMPLATE_VERSION,
        )
        return record

    async def list_for_application(
        self,
        application_id: UUID,
    ) -> list[GeneratedDocument]:
        await self._applications.get(application_id)
        result = await self._session.execute(
            select(GeneratedDocument)
            .where(GeneratedDocument.application_id == application_id)
            .order_by(GeneratedDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_download(
        self,
        application_id: UUID,
        document_id: UUID,
    ) -> tuple[GeneratedDocument, Path]:
        result = await self._session.execute(
            select(GeneratedDocument).where(GeneratedDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        if (
            document is None
            or document.application_id != application_id
            or document.generation_status != DocumentGenerationStatus.SUCCESS
            or not document.storage_key
        ):
            raise DocumentNotFoundError()
        try:
            path = resolve_storage_path(documents_root(), document.storage_key)
        except UnsafeStorageKeyError as exc:
            raise DocumentNotFoundError() from exc
        if not path.is_file():
            raise DocumentNotFoundError()
        return document, path
