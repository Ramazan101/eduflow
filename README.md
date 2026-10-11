# EduFlow

Student admissions workspace: FastAPI, Next.js, PostgreSQL.

This repository includes a **local judging / demo** Docker Compose stack. It has not been reviewed or tested as a production deployment.

## Local Docker demo (judges)

Requires Docker Compose v2 (health checks and `service_completed_successfully`).

```bash
./scripts/prepare-env.sh
docker compose build
docker compose up -d
./scripts/demo-init.sh
```

`prepare-env.sh` writes a gitignored `.env` with generated `SECRET_KEY`, `POSTGRES_PASSWORD`, and `BOOTSTRAP_ADMIN_PASSWORD`. It does not overwrite an existing `.env`.

`demo-init.sh` seeds a synthetic institution (skipped if `northstar-academy` already exists) and creates the first administrator (skipped if any administrator row exists). Neither command runs on ordinary container restart.

- Applicant: http://localhost:3000/apply
- Registrar: http://localhost:3000/admin/login  
  Email: `BOOTSTRAP_ADMIN_EMAIL` in `.env` (default `registrar@example.edu`)  
  Password: `BOOTSTRAP_ADMIN_PASSWORD` in `.env`

Migrations run in the one-shot `migrate` service (`alembic upgrade head`) after Postgres is healthy, before the API starts. Generated PDFs live on the `backend_documents` volume under `/app/storage/documents` and are not served as static files. Postgres is not published on the host; only the API (`8000`) and UI (`3000`) are.

### Reset the demo database

This deletes the database volume **and** stored demo PDFs:

```bash
docker compose down -v
docker compose up -d
./scripts/demo-init.sh
```

Then sign in with the credentials currently in `.env` (bootstrap only creates an admin when the table is empty).

## Host development (without Compose)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set SECRET_KEY to a random value of at least 32 characters.
alembic upgrade head
python -m app.seed_catalog
export BOOTSTRAP_ADMIN_EMAIL="registrar@example.edu"
export BOOTSTRAP_ADMIN_PASSWORD="choose-a-long-unique-password"
python -m app.bootstrap
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`seed_catalog` loads a synthetic development institution. It does not create applications.

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

`NEXT_PUBLIC_API_URL` is the public API origin. Do not put secrets in frontend env files.

## Checks

```bash
cd backend && pytest
cd frontend && npm run lint && npm run typecheck && npm run build
```

There is no frontend unit-test suite. `pytest` uses the host `DATABASE_URL` in `backend/.env` (or the test fallback). Do not point it at the Compose database; the suite truncates tables.

A generated PDF is a demo summary, not a signed offer or enrollment record.
