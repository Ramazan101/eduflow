from functools import lru_cache

from pydantic import AliasChoices, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Secrets are never defaulted to production values."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    project_name: str = "EduFlow"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    database_url: str = Field(
        ...,
        min_length=1,
        description="SQLAlchemy async URL, e.g. postgresql+asyncpg://user:pass@host:5432/db",
    )
    secret_key: str = Field(
        ...,
        min_length=32,
        description="HMAC secret for signing administrator access tokens.",
    )
    access_token_expire_minutes: int = Field(default=60, ge=5, le=1440)
    document_storage_dir: str = "storage/documents"
    allow_admin_bootstrap: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "ALLOW_ADMIN_BOOTSTRAP",
            "EDUFLOW_ALLOW_ADMIN_BOOTSTRAP",
        ),
    )

    @field_validator("database_url")
    @classmethod
    def database_url_must_be_asyncpg(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must start with postgresql+asyncpg:// "
                "(example: postgresql+asyncpg://eduflow:eduflow@127.0.0.1:5432/eduflow)"
            )
        return value

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_random(cls, value: str) -> str:
        stripped = value.strip()
        lowered = stripped.lower()
        if lowered in {
            "changeme",
            "change-me",
            "secret",
            "password",
            "replace-with-a-long-random-value-at-least-32-chars",
        }:
            raise ValueError("SECRET_KEY must be a unique random value, not a placeholder")
        return stripped

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


def load_settings(*, env_file: str | None = ".env") -> Settings:
    try:
        return Settings(_env_file=env_file)
    except ValidationError as exc:
        raise RuntimeError(
            "Invalid EduFlow configuration. Set DATABASE_URL to a "
            "postgresql+asyncpg:// connection string and SECRET_KEY to a random "
            "value of at least 32 characters. See backend/.env.example."
        ) from exc


@lru_cache
def get_settings() -> Settings:
    return load_settings()
