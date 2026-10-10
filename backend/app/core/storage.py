import re
from pathlib import Path

from app.core.config import get_settings
from app.services.exceptions import UnsafeStorageKeyError

STORAGE_KEY_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.pdf$"
)


def backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def documents_root() -> Path:
    settings = get_settings()
    path = Path(settings.document_storage_dir)
    if not path.is_absolute():
        path = backend_root() / path
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def resolve_storage_path(root: Path, storage_key: str) -> Path:
    """Map an opaque storage key to a file under root. Rejects traversal."""
    if not STORAGE_KEY_PATTERN.fullmatch(storage_key):
        raise UnsafeStorageKeyError()
    base = root.resolve()
    candidate = (base / storage_key).resolve()
    if not candidate.is_relative_to(base):
        raise UnsafeStorageKeyError()
    return candidate
