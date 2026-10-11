from pathlib import Path

import pytest

from app.core.storage import resolve_storage_path
from app.services.exceptions import UnsafeStorageKeyError


def test_resolve_storage_path_accepts_opaque_pdf_key(tmp_path: Path) -> None:
    key = "11111111-1111-1111-1111-111111111111.pdf"
    resolved = resolve_storage_path(tmp_path, key)
    assert resolved.parent == tmp_path.resolve()
    assert resolved.name == key


@pytest.mark.parametrize(
    "key",
    [
        "../secret.pdf",
        "..%2fsecret.pdf",
        "/etc/passwd",
        "subdir/11111111-1111-1111-1111-111111111111.pdf",
        "11111111-1111-1111-1111-111111111111.pdf/../secret",
        "",
        "contract.pdf",
    ],
)
def test_resolve_storage_path_rejects_traversal(tmp_path: Path, key: str) -> None:
    with pytest.raises(UnsafeStorageKeyError):
        resolve_storage_path(tmp_path, key)
