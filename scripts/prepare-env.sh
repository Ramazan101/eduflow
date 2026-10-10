#!/usr/bin/env sh
# Create a gitignored .env for local Compose. Never overwrites an existing file.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT"

if [ -f .env ]; then
  echo ".env already exists; leaving it unchanged."
  exit 0
fi

if [ ! -f .env.example ]; then
  echo "Missing .env.example" >&2
  exit 1
fi

python3 - "$ROOT" <<'PY'
import secrets
import sys
from pathlib import Path

root = Path(sys.argv[1])
example = (root / ".env.example").read_text(encoding="utf-8")
fills = {
    "POSTGRES_PASSWORD": secrets.token_hex(24),
    "SECRET_KEY": secrets.token_hex(32),
    "BOOTSTRAP_ADMIN_PASSWORD": secrets.token_hex(16),
}
lines = []
for line in example.splitlines():
    if not line or line.lstrip().startswith("#") or "=" not in line:
        lines.append(line)
        continue
    key, _, value = line.partition("=")
    if key in fills and not value.strip():
        lines.append(f"{key}={fills[key]}")
    else:
        lines.append(line)
(root / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Wrote .env with generated POSTGRES_PASSWORD, SECRET_KEY, and BOOTSTRAP_ADMIN_PASSWORD.")
print("Do not commit .env. Registrar password is BOOTSTRAP_ADMIN_PASSWORD in that file.")
PY
