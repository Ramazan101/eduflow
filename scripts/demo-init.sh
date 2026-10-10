#!/usr/bin/env sh
# Idempotent catalog seed + first administrator. Requires a healthy backend/db.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT"

if [ ! -f .env ]; then
  echo "Missing .env. Run ./scripts/prepare-env.sh first." >&2
  exit 1
fi

docker compose run --rm --no-deps backend python -m app.seed_catalog
docker compose run --rm --no-deps backend python -m app.bootstrap

email=$(python3 -c "from pathlib import Path
for line in Path('.env').read_text().splitlines():
    if line.startswith('BOOTSTRAP_ADMIN_EMAIL='):
        print(line.split('=',1)[1]); break")
echo "Registrar email: ${email}"
echo "Password is BOOTSTRAP_ADMIN_PASSWORD in .env (not printed)."
