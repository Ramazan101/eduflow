# EduFlow

B2B student onboarding: FastAPI backend, Next.js frontend, PostgreSQL.

## Run with Docker

From the repository root:

```bash
docker-compose up --build
```

This starts three services:

| Service | URL |
| --- | --- |
| Frontend (student apply + admin) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| PostgreSQL | localhost:5432 |

- Student application: http://localhost:3000/apply
- Admin dashboard: http://localhost:3000/admin
- API docs: http://localhost:8000/docs

The backend waits for Postgres to be healthy, then runs `alembic upgrade head` before Uvicorn. The browser talks to the API at `http://localhost:8000` (`NEXT_PUBLIC_API_URL`).

Stop the stack with `Ctrl+C`, or `docker-compose down`. Add `-v` to also remove the database volume.
