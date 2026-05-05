# VetShield AI

Production-oriented MVP foundation for a veterinary reputation monitoring SaaS.

This repository currently contains the backend foundation only:

- FastAPI application
- PostgreSQL-ready SQLAlchemy setup
- SQLAlchemy MVP domain models
- Alembic migration setup
- Redis + RQ worker setup
- Mock AI provider
- Mock email provider
- Docker Compose for local development
- Minimal health checks

## Why RQ?

RQ is used instead of Celery for the MVP because it is simpler to operate locally, has fewer concepts, and is enough for early background jobs such as AI analysis, alert emails, and review request scheduling. Celery can be introduced later if the system needs complex routing, retries, workflows, or high-volume scheduling.

## Requirements

- Docker
- Docker Compose

For local development without Docker:

- Python 3.12+
- PostgreSQL
- Redis

## Local Setup With Docker

1. Create your environment file:

```bash
cp .env.example .env
```

2. Start the local stack:

```bash
docker compose up --build
```

3. Run database migrations:

```bash
docker compose exec api alembic upgrade head
```

4. Open the API health check:

```text
http://localhost:8000/health
```

5. Open the generated API docs:

```text
http://localhost:8000/docs
```

## Services

Docker Compose starts:

- `api`: FastAPI backend on port `8000`
- `worker`: RQ background worker
- `postgres`: PostgreSQL database on port `5432`
- `redis`: Redis broker on port `6379`

## Local Setup Without Docker

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run a worker in another terminal:

```bash
cd backend
.venv\Scripts\activate
rq worker default ai notifications review_requests
```

## Project Structure

```text
backend/
  app/
    api/
      routes/
    core/
    db/
      models/
      migrations/
    integrations/
      ai/
      email/
    modules/
    workers/
    main.py
  requirements.txt
  Dockerfile
docker-compose.yml
.env.example
```

## Current Scope

Implemented:

- application bootstrap
- settings management
- database engine/session setup
- MVP SQLAlchemy models
- initial Alembic migration
- Redis/RQ connection setup
- mock AI provider
- mock email provider
- health endpoints
- JWT authentication and clinic membership authorization
- clinic, keyword, mention, AI analysis, and alert MVP endpoints

Intentionally not implemented yet:

- review request workflows
- real external integrations
- billing

## Health Endpoints

- `GET /health/live`: confirms the API process is running
- `GET /health/ready`: checks PostgreSQL and Redis connectivity
- `GET /health`: combined health summary

## MVP API Endpoints

Auth:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Clinics:

- `GET /api/v1/clinics`
- `POST /api/v1/clinics`
- `GET /api/v1/clinics/{clinic_id}`
- `PATCH /api/v1/clinics/{clinic_id}`
- `DELETE /api/v1/clinics/{clinic_id}`

Keywords:

- `GET /api/v1/clinics/{clinic_id}/keywords`
- `POST /api/v1/clinics/{clinic_id}/keywords`
- `GET /api/v1/keywords/{keyword_id}`
- `PATCH /api/v1/keywords/{keyword_id}`
- `DELETE /api/v1/keywords/{keyword_id}`

Mentions:

- `GET /api/v1/clinics/{clinic_id}/mentions`
- `POST /api/v1/clinics/{clinic_id}/mentions`
- `GET /api/v1/mentions/{mention_id}`
- `PATCH /api/v1/mentions/{mention_id}`
- `DELETE /api/v1/mentions/{mention_id}`

AI analysis and alerts:

- `GET /api/v1/mentions/{mention_id}/ai-analysis`
- `GET /api/v1/clinics/{clinic_id}/alerts`

All MVP business endpoints require a bearer token. Users can only access clinics where they have a `clinic_members` row; creating a clinic automatically creates an owner membership for the current user.

## Database Migrations

Run migrations from Docker:

```bash
docker compose exec api alembic upgrade head
```

Create a future migration after changing models:

```bash
docker compose exec api alembic revision --autogenerate -m "describe change"
```

Run migrations locally without Docker from the `backend` directory:

```bash
alembic upgrade head
```

## Tests

Run tests with Docker:

```bash
docker compose exec api python -m pytest
```

Or locally from the repository root:

```bash
python -m pytest backend/tests
```

## Development Notes

This project follows the MVP guidance from `AGENTS.md`:

- no scraping of restricted/private data
- no auto-publishing of AI responses
- mock integrations first
- modular architecture
- human approval required for sensitive actions
- compliance-conscious defaults

## License

This project is proprietary software. All rights reserved.

The source code may not be copied, modified, distributed, or used without prior written permission from the copyright holder.
