# EduFlow frontend

Next.js 14 applicant portal and registrar workspace. Talks to the FastAPI backend.

For Docker Compose judging, use the repository root `README.md`.

## Run

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

`NEXT_PUBLIC_API_URL` is the public API origin (default `http://localhost:8000`). Do not put secrets in frontend env files.

The backend must already have:

```bash
cd backend
alembic upgrade head
python -m app.seed_catalog
python -m app.bootstrap   # with BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Checks

```bash
npm run lint
npm run typecheck
npm run build
```

There is no frontend unit-test suite in this milestone.
