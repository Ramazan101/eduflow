import pytest

from app.core.config import load_settings


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        load_settings(env_file=None)


def test_database_url_must_use_asyncpg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://eduflow:eduflow@127.0.0.1:5432/eduflow")
    with pytest.raises(RuntimeError, match="postgresql\\+asyncpg"):
        load_settings(env_file=None)


def test_secret_key_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://eduflow:eduflow@127.0.0.1:5432/eduflow",
    )
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        load_settings(env_file=None)


def test_secret_key_rejects_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://eduflow:eduflow@127.0.0.1:5432/eduflow",
    )
    monkeypatch.setenv(
        "SECRET_KEY",
        "replace-with-a-long-random-value-at-least-32-chars",
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        load_settings(env_file=None)


def test_valid_settings_expose_cors_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://eduflow:eduflow@127.0.0.1:5432/eduflow",
    )
    monkeypatch.setenv(
        "SECRET_KEY",
        "eduflow-test-secret-key-not-for-production-use",
    )
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, http://127.0.0.1:3000")
    settings = load_settings(env_file=None)
    assert settings.cors_origin_list == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    assert "password" not in settings.model_dump()
