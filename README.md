# Vet Reputation AI

Production-oriented MVP foundation for a veterinary reputation monitoring SaaS.

This repository currently contains the backend foundation only:

- FastAPI application
- PostgreSQL-ready SQLAlchemy setup
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

3. Open the API health check:

```text
http://localhost:8000/health
```

4. Open the generated API docs:

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
- Redis/RQ connection setup
- mock AI provider
- mock email provider
- health endpoints

Intentionally not implemented yet:

- authentication
- clinic accounts
- keyword management
- mentions
- alert business logic
- review request workflows
- real external integrations
- billing

## Health Endpoints

- `GET /health/live`: confirms the API process is running
- `GET /health/ready`: checks PostgreSQL and Redis connectivity
- `GET /health`: combined health summary

## Development Notes

This project follows the MVP guidance from `AGENTS.md`:

- no scraping of restricted/private data
- no auto-publishing of AI responses
- mock integrations first
- modular architecture
- human approval required for sensitive actions
- compliance-conscious defaults
