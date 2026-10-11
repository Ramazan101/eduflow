from datetime import date
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ApplicationStatus
from tests.helpers import (
    TEST_ADMIN_EMAIL,
    TEST_ADMIN_PASSWORD,
    seed_admin,
    seed_verified_catalog,
)

pytestmark = pytest.mark.usefixtures("truncate_tables")

SYNTHETIC_PHONE = "+77011234567"


def _application_body(program_id, profile_id, email: str = "amina@example.edu") -> dict:
    return {
        "program_id": str(program_id),
        "requirement_profile_id": str(profile_id),
        "applicant_name": "Amina Karimova",
        "birth_date": "2004-03-12",
        "phone": SYNTHETIC_PHONE,
        "email": email,
    }


async def _auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _assert_no_secrets(payload: str) -> None:
    lowered = payload.lower()
    assert "hashed_password" not in lowered
    assert "secret_key" not in lowered
    assert "argon2" not in lowered
    assert "postgresql+" not in lowered


@pytest.mark.asyncio
async def test_login_rejects_unknown_and_wrong_password_with_same_detail(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    await seed_admin(db_session)
    missing = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.edu", "password": TEST_ADMIN_PASSWORD},
    )
    wrong = await client.post(
        "/api/v1/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": "definitely-not-the-password"},
    )
    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert missing.json() == wrong.json() == {"detail": "Invalid credentials"}
    _assert_no_secrets(missing.text)
    _assert_no_secrets(wrong.text)


@pytest.mark.asyncio
async def test_unauthenticated_admin_requests_are_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, program, profile = await seed_verified_catalog(db_session)
    created = await client.post(
        "/api/v1/applications/",
        json=_application_body(program.id, profile.id),
    )
    assert created.status_code == 201
    application_id = created.json()["id"]

    listing = await client.get("/api/v1/applications/")
    detail = await client.get(f"/api/v1/applications/{application_id}")
    status_view = await client.get(f"/api/v1/applications/{application_id}/status")
    transition = await client.post(
        f"/api/v1/applications/{application_id}/status",
        json={"status": "PENDING_REVIEW"},
    )
    for response in (listing, detail, status_view, transition):
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}
        _assert_no_secrets(response.text)


@pytest.mark.asyncio
async def test_public_applicant_cannot_read_another_record(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, program, profile = await seed_verified_catalog(db_session)
    created = await client.post(
        "/api/v1/applications/",
        json=_application_body(program.id, profile.id),
    )
    application_id = created.json()["id"]
    response = await client.get(f"/api/v1/applications/{application_id}")
    assert response.status_code == 401
    missing = await client.get(f"/api/v1/applications/{uuid4()}")
    assert missing.status_code == 401
    assert response.json() == missing.json()


@pytest.mark.asyncio
async def test_authenticated_admin_can_list_get_and_transition(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await seed_admin(db_session)
    _, program, profile = await seed_verified_catalog(db_session)
    created = await client.post(
        "/api/v1/applications/",
        json=_application_body(program.id, profile.id),
    )
    assert created.status_code == 201
    body = created.json()
    assert set(body.keys()) == {"id", "status"}
    assert body["status"] == "NEW"
    application_id = body["id"]

    headers = await _auth_header(client)
    listing = await client.get(
        "/api/v1/applications/",
        params={"status": "NEW", "limit": 20, "offset": 0},
        headers=headers,
    )
    assert listing.status_code == 200
    page = listing.json()
    assert page["total"] == 1
    assert page["items"][0]["id"] == application_id
    assert "admin_notes" not in page["items"][0]
    assert "hashed_password" not in listing.text

    detail = await client.get(f"/api/v1/applications/{application_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["applicant_name"] == "Amina Karimova"
    assert detail.json()["email"] == "amina@example.edu"

    invalid = await client.post(
        f"/api/v1/applications/{application_id}/status",
        json={"status": "ACCEPTED"},
        headers=headers,
    )
    assert invalid.status_code == 409

    pending = await client.post(
        f"/api/v1/applications/{application_id}/status",
        json={"status": "PENDING_REVIEW", "note": "Ready for registrar review"},
        headers=headers,
    )
    assert pending.status_code == 200
    assert pending.json()["status"] == "PENDING_REVIEW"

    status_payload = await client.get(
        f"/api/v1/applications/{application_id}/status",
        headers=headers,
    )
    assert status_payload.status_code == 200
    history = status_payload.json()["status_history"]
    assert [row["to_status"] for row in history] == ["NEW", "PENDING_REVIEW"]
    assert history[0]["changed_by_id"] is None
    assert history[1]["changed_by_id"] == str(admin.id)
    assert status_payload.json()["status"] == "PENDING_REVIEW"


@pytest.mark.asyncio
async def test_malformed_input_is_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, program, profile = await seed_verified_catalog(db_session)
    response = await client.post(
        "/api/v1/applications/",
        json={
            **_application_body(program.id, profile.id),
            "phone": "77011234567",
            "passport_number": "N12345678",
        },
    )
    assert response.status_code == 400
    _assert_no_secrets(response.text)


@pytest.mark.asyncio
async def test_application_creation_persists_and_catalog_lists_verified_only(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    institution, program, profile = await seed_verified_catalog(db_session)
    created = await client.post(
        "/api/v1/applications/",
        json=_application_body(program.id, profile.id),
    )
    assert created.status_code == 201

    institutions = await client.get("/api/v1/institutions")
    programs = await client.get("/api/v1/programs")
    profiles = await client.get("/api/v1/requirement-profiles")
    assert institutions.status_code == 200
    assert programs.status_code == 200
    assert profiles.status_code == 200
    institution_ids = {item["id"] for item in institutions.json()}
    program_ids = {item["id"] for item in programs.json()}
    profile_payload = next(
        item for item in profiles.json() if item["id"] == str(profile.id)
    )
    assert str(institution.id) in institution_ids
    assert str(program.id) in program_ids
    assert "approval_reference" not in profile_payload
    assert "notes" not in profile_payload
    assert profile_payload["institution_id"] == str(institution.id)

    await seed_admin(db_session)
    headers = await _auth_header(client)
    listing = await client.get("/api/v1/applications/", headers=headers)
    item = listing.json()["items"][0]
    assert item["phone"] == SYNTHETIC_PHONE
    assert item["birth_date"] == "2004-03-12"
    assert date.fromisoformat(item["birth_date"]).year == 2004


@pytest.mark.asyncio
async def test_inactive_admin_token_is_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await seed_admin(db_session)
    headers = await _auth_header(client)
    admin.is_active = False
    await db_session.commit()
    response = await client.get("/api/v1/applications/", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized"}
