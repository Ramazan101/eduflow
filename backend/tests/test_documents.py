from datetime import date
from io import BytesIO
from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import AsyncClient
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.storage import documents_root
from app.models.document import GeneratedDocument
from app.models.enums import ApplicationStatus, DocumentGenerationStatus
from app.schemas.application import ApplicationCreate
from app.services.application import ApplicationService
from app.services.document import (
    DEMO_DISCLAIMER,
    TEMPLATE_KEY,
    TEMPLATE_VERSION,
    DocumentService,
    build_document_context,
)
from app.services.exceptions import (
    PdfGenerationError,
    TemplateDataError,
    TemplateUnavailableError,
)
from tests.helpers import auth_header, seed_admin, seed_verified_catalog

pytestmark = pytest.mark.usefixtures("truncate_tables")


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    get_settings.cache_clear()
    yield tmp_path
    get_settings.cache_clear()


def _payload(program_id, profile_id) -> ApplicationCreate:
    return ApplicationCreate(
        program_id=program_id,
        requirement_profile_id=profile_id,
        applicant_name="Amina Karimova",
        birth_date=date(2004, 3, 12),
        phone="+77011234567",
        email="amina@example.edu",
    )


async def _create_application(db_session: AsyncSession):
    _, program, profile = await seed_verified_catalog(db_session)
    application = await ApplicationService(db_session).create(
        _payload(program.id, profile.id)
    )
    return application


def test_build_document_context_requires_fields() -> None:
    incomplete = SimpleNamespace(
        id=uuid4(),
        applicant_name="",
        birth_date=date(2004, 3, 12),
        phone="+77011234567",
        email="amina@example.edu",
        status=ApplicationStatus.NEW,
        program=SimpleNamespace(
            name="Computer Science",
            institution=SimpleNamespace(name="Northstar Academy"),
        ),
        requirement_profile=SimpleNamespace(name="Undergraduate 2026"),
    )
    with pytest.raises(TemplateDataError):
        build_document_context(incomplete)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_successful_generation_and_authorized_download(
    client: AsyncClient,
    db_session: AsyncSession,
    isolated_storage,
) -> None:
    await seed_admin(db_session)
    application = await _create_application(db_session)
    headers = await auth_header(client)
    status_before = application.status

    created = await client.post(
        f"/api/v1/applications/{application.id}/documents",
        headers=headers,
    )
    assert created.status_code == 201, created.text
    meta = created.json()
    assert meta["template_key"] == TEMPLATE_KEY
    assert meta["template_version"] == TEMPLATE_VERSION
    assert meta["application_id"] == str(application.id)
    assert meta["generation_status"] == "SUCCESS"
    assert "storage_key" not in meta
    assert "/home/" not in created.text
    assert "storage/" not in created.text

    refreshed = await ApplicationService(db_session).get(application.id)
    assert refreshed.status == status_before

    listing = await client.get(
        f"/api/v1/applications/{application.id}/documents",
        headers=headers,
    )
    assert listing.status_code == 200
    assert listing.json()[0]["id"] == meta["id"]

    download = await client.get(
        f"/api/v1/applications/{application.id}/documents/{meta['id']}/download",
        headers=headers,
    )
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/pdf")
    assert download.content.startswith(b"%PDF-")
    text = "".join(page.extract_text() or "" for page in PdfReader(BytesIO(download.content)).pages)
    assert DEMO_DISCLAIMER in text
    assert "Amina Karimova" in text
    assert TEMPLATE_VERSION in text
    assert "not an offer, contract, enrollment confirmation" in text.lower() or (
        "not an offer" in text.lower()
    )


@pytest.mark.asyncio
async def test_unauthorized_download_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
    isolated_storage,
) -> None:
    admin = await seed_admin(db_session)
    application = await _create_application(db_session)
    document = await DocumentService(db_session).generate(application.id, admin)
    response = await client.get(
        f"/api/v1/applications/{application.id}/documents/{document.id}/download",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_document_from_other_application_is_not_downloadable(
    client: AsyncClient,
    db_session: AsyncSession,
    isolated_storage,
) -> None:
    await seed_admin(db_session)
    first = await _create_application(db_session)
    second = await _create_application(db_session)
    headers = await auth_header(client)
    created = await client.post(
        f"/api/v1/applications/{first.id}/documents",
        headers=headers,
    )
    document_id = created.json()["id"]
    response = await client.get(
        f"/api/v1/applications/{second.id}/documents/{document_id}/download",
        headers=headers,
    )
    assert response.status_code == 404
    assert "storage" not in response.text.lower()
    assert "/home/" not in response.text


@pytest.mark.asyncio
async def test_path_traversal_download_is_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
    isolated_storage,
) -> None:
    await seed_admin(db_session)
    application = await _create_application(db_session)
    headers = await auth_header(client)
    response = await client.get(
        f"/api/v1/applications/{application.id}/documents/../secrets/download",
        headers=headers,
    )
    assert response.status_code in {400, 404, 405, 422}


@pytest.mark.asyncio
async def test_invalid_template_records_failure_without_status_change(
    db_session: AsyncSession,
    isolated_storage,
) -> None:
    admin = await seed_admin(db_session)
    application = await _create_application(db_session)
    application_id = application.id
    service = DocumentService(
        db_session,
        template_filename="does_not_exist.html",
    )
    with pytest.raises(TemplateUnavailableError):
        await service.generate(application_id, admin)

    refreshed = await ApplicationService(db_session).get(application_id)
    assert refreshed.status == ApplicationStatus.NEW
    rows = (
        await db_session.execute(
            select(GeneratedDocument).where(
                GeneratedDocument.application_id == application_id
            )
        )
    ).scalars().all()
    assert len(rows) == 1
    assert rows[0].generation_status == DocumentGenerationStatus.FAILED
    assert rows[0].error_code == "TEMPLATE_UNAVAILABLE"
    assert rows[0].storage_key is None
    assert list(documents_root().glob("*.pdf")) == []


@pytest.mark.asyncio
async def test_render_failure_is_not_reported_as_success(
    db_session: AsyncSession,
    isolated_storage,
) -> None:
    admin = await seed_admin(db_session)
    application = await _create_application(db_session)
    application_id = application.id

    def boom(_html: str, _path) -> None:
        raise RuntimeError("renderer exploded")

    service = DocumentService(db_session, write_pdf_fn=boom)
    with pytest.raises(PdfGenerationError):
        await service.generate(application_id, admin)

    refreshed = await ApplicationService(db_session).get(application_id)
    assert refreshed.status == ApplicationStatus.NEW
    rows = (
        await db_session.execute(
            select(GeneratedDocument).where(
                GeneratedDocument.application_id == application_id
            )
        )
    ).scalars().all()
    assert rows[0].generation_status == DocumentGenerationStatus.FAILED
    assert rows[0].error_code == "RENDER_FAILED"
    assert list(isolated_storage.glob("*.pdf")) == []


@pytest.mark.asyncio
async def test_missing_template_data_is_rejected(
    db_session: AsyncSession,
    isolated_storage,
) -> None:
    admin = await seed_admin(db_session)
    application = await _create_application(db_session)
    application_id = application.id
    application.applicant_name = ""
    db_session.add(application)
    await db_session.commit()

    with pytest.raises(TemplateDataError):
        await DocumentService(db_session).generate(application_id, admin)

    rows = (
        await db_session.execute(
            select(GeneratedDocument).where(
                GeneratedDocument.application_id == application_id
            )
        )
    ).scalars().all()
    assert rows[0].generation_status == DocumentGenerationStatus.FAILED
    assert rows[0].error_code == "MISSING_TEMPLATE_DATA"
    refreshed = await ApplicationService(db_session).get(application_id)
    assert refreshed.status == ApplicationStatus.NEW
