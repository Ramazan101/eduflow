from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.program import Program
    from app.models.requirement_profile import RequirementProfile


class Institution(Base):
    __tablename__ = "institutions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    programs: Mapped[list["Program"]] = relationship(back_populates="institution")
    requirement_profiles: Mapped[list["RequirementProfile"]] = relationship(
        back_populates="institution",
    )
