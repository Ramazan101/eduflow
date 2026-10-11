"""Load a synthetic development catalog. Does not create applications or admins."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate
from app.schemas.program import ProgramCreate
from app.schemas.requirement_profile import (
    RequirementProfileCreate,
    RequirementProfileVerify,
)
from app.services.catalog import CatalogService

DEMO_SLUG = "northstar-academy"


async def seed_catalog() -> int:
    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(Institution).where(Institution.slug == DEMO_SLUG)
        )
        if existing.scalar_one_or_none() is not None:
            print("Synthetic catalog already present. No changes made.")
            return 0

        catalog = CatalogService(session)
        institution = await catalog.create_institution(
            InstitutionCreate(name="Northstar Academy", slug=DEMO_SLUG)
        )
        program = await catalog.create_program(
            ProgramCreate(
                institution_id=institution.id,
                name="Computer Science",
                is_active=True,
            )
        )
        profile = await catalog.create_requirement_profile(
            RequirementProfileCreate(
                institution_id=institution.id,
                name="Undergraduate admissions 2026",
                source_reference="https://example.edu/admissions/ug-2026",
                notes="Synthetic development profile. Not an official policy document.",
            )
        )
        await catalog.verify_requirement_profile(
            profile.id,
            RequirementProfileVerify(approval_reference="SYNTHETIC-REG-2026-01"),
        )
        print(
            f"Seeded {institution.name}: program {program.name} "
            f"({program.id}), profile {profile.name} ({profile.id})."
        )
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(seed_catalog()))


if __name__ == "__main__":
    main()
