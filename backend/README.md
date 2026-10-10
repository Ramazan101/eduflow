# EduFlow backend

FastAPI application with PostgreSQL, SQLAlchemy 2, and Alembic.

For the local Compose demo used in judging, see the repository root `README.md`. Do not treat this service as production-ready.

Milestone 3 adds demo PDF generation with WeasyPrint and Jinja2. Generated files are not legal documents and do not change application status.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ with a database and role that match `DATABASE_URL`

Create a database (example):

```bash
sudo -u postgres psql -c "CREATE USER eduflow WITH PASSWORD 'eduflow';"
sudo -u postgres psql -c "CREATE DATABASE eduflow OWNER eduflow;"
```

## Install dependencies

From `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `SECRET_KEY` to a random value of at least 32 characters (the example file leaves it empty on purpose). `DATABASE_URL` must use the `postgresql+asyncpg://` scheme.

## Run migrations

From `backend/` with the virtualenv active:

```bash
alembic upgrade head
```

Do not use SQLAlchemy `create_all` to create tables.

## Bootstrap the first administrator

This does **not** run when the API starts. It creates one administrator only when the table is empty. There is no built-in password.

```bash
export BOOTSTRAP_ADMIN_EMAIL="registrar@example.edu"
export BOOTSTRAP_ADMIN_PASSWORD="choose-a-long-unique-password"
python -m app.bootstrap
```

In `ENVIRONMENT=production` the command exits unless `ALLOW_ADMIN_BOOTSTRAP=true` (or `EDUFLOW_ALLOW_ADMIN_BOOTSTRAP=true`).

## Start the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET /health`
- Public submit: `POST /api/v1/applications/`
- Admin login: `POST /api/v1/auth/login`
- Admin list/detail/status: `Authorization: Bearer <access_token>`
- Demo PDF (admin): `POST /api/v1/applications/{id}/documents` then
  `GET /api/v1/applications/{id}/documents/{document_id}/download`

No approved institution template is in this repository. The shipped template is a demo
summary marked **DEMO — NOT A LEGAL DOCUMENT — NOT FOR SIGNING**. A generated PDF is
not enrollment, payment, approval, or a signature.

## Run tests

```bash
pytest
```

Tests use synthetic applicant and administrator data only.

## Authentication approach

Administrators are stored in the `administrators` table. Passwords are hashed with Argon2id (`argon2-cffi`). Login issues a signed JWT (`HS256`) whose subject is the administrator id. Administrative routes require that token and then load an **active** row from the table. A role field on the client is never trusted. Public applicants may submit an application; they cannot list or fetch records.

### Risks

- JWTs are not revoked before expiry. Compromised tokens remain valid until `ACCESS_TOKEN_EXPIRE_MINUTES`.
- HS256 depends on `SECRET_KEY`. If that secret leaks, tokens can be forged.
- Bearer tokens stored in browser JavaScript are exposed to XSS. Prefer an httpOnly cookie in a later frontend milestone.
- Login is not rate-limited yet. Brute-force protection is still required for production.
- The bootstrap command is powerful. Keep `BOOTSTRAP_ADMIN_PASSWORD` out of git and disable `ALLOW_ADMIN_BOOTSTRAP` after the first account exists.
