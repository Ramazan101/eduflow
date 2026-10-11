from datetime import date, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.application import ApplicationCreate
from app.schemas.institution import InstitutionCreate
from app.schemas.requirement_profile import RequirementProfileCreate


def test_application_rejects_invalid_phone() -> None:
    with pytest.raises(ValidationError):
        ApplicationCreate(
            program_id=uuid4(),
            requirement_profile_id=uuid4(),
            applicant_name="Amina Karimova",
            birth_date=date(2004, 3, 12),
            phone="77011234567",
            email="amina@example.edu",
        )


def test_application_rejects_future_birth_date() -> None:
    with pytest.raises(ValidationError, match="birth_date"):
        ApplicationCreate(
            program_id=uuid4(),
            requirement_profile_id=uuid4(),
            applicant_name="Amina Karimova",
            birth_date=date.today() + timedelta(days=1),
            phone="+77011234567",
            email="amina@example.edu",
        )


def test_application_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ApplicationCreate.model_validate(
            {
                "program_id": str(uuid4()),
                "requirement_profile_id": str(uuid4()),
                "applicant_name": "Amina Karimova",
                "birth_date": "2004-03-12",
                "phone": "+77011234567",
                "email": "amina@example.edu",
                "passport_number": "N12345678",
            }
        )


def test_application_accepts_valid_payload() -> None:
    payload = ApplicationCreate(
        program_id=uuid4(),
        requirement_profile_id=uuid4(),
        applicant_name="Amina Karimova",
        birth_date=date(2004, 3, 12),
        phone="+77011234567",
        email="amina@example.edu",
    )
    assert payload.phone == "+77011234567"


def test_institution_slug_must_be_lowercase() -> None:
    with pytest.raises(ValidationError):
        InstitutionCreate(name="Northstar Academy", slug="Northstar")


def test_requirement_profile_requires_source_reference() -> None:
    with pytest.raises(ValidationError):
        RequirementProfileCreate(
            institution_id=uuid4(),
            name="Undergraduate 2026",
            source_reference="",
        )
