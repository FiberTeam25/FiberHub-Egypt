# FiberHub Egypt

B2B platform for Egypt's fiber optic sector.

## Tech Stack

- **Backend**: FastAPI + Python 3.11 + SQLAlchemy 2.0 (async) + Alembic
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (not yet scaffolded)
- **Database**: PostgreSQL 16
- **Storage**: S3/MinIO
- **Cache/Queue**: Redis + arq
- **Dev Email**: MailHog

## Project Structure

```
backend/           FastAPI backend
  app/             Application code
    auth/          Authentication (JWT, register, login)
    users/         User CRUD
    companies/     Company profiles, members, services, products
    categories/    Product/service categories, governorates
    profiles/      Individual professional profiles (stub)
    search/        Search API (stub)
    verification/  Verification workflow (stub)
    rfqs/          RFQ workflow (stub)
    messages/      Messaging (stub)
    reviews/       Reviews & ratings (stub)
    notifications/ Notifications (stub)
    admin/         Admin dashboard (stub)
    models/        All SQLAlchemy models
    storage/       S3/MinIO file operations
    workers/       Background tasks (email, notifications)
  alembic/         Database migrations
  scripts/         CLI utilities (seed, create admin)
  tests/           Pytest test suite
frontend/          Next.js frontend (not yet scaffolded)
```

## Local Development

```bash
# Start infrastructure
docker compose up -d db redis minio minio-init mailhog

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed_categories
python -m scripts.create_superadmin --email admin@fiberhub.eg --password Admin123!
uvicorn app.main:app --reload

# API docs: http://localhost:8000/api/v1/docs
# MailHog UI: http://localhost:8025
# MinIO console: http://localhost:9001 (minioadmin/minioadmin)
```

## Architecture Patterns

- **Service layer** handles business logic (e.g., `companies/service.py`)
- **Repository layer** handles database queries (e.g., `companies/repository.py`)
- **Router** defines endpoints and wires dependencies
- **Schemas** (Pydantic) for request/response validation
- **Models** (SQLAlchemy) for database tables
- Auth via JWT Bearer tokens; `CurrentUser` / `AdminUser` dependency annotations

## Conventions

- UUIDs as string primary keys
- Async everywhere (asyncpg, async SQLAlchemy)
- `get_db` dependency in `app/dependencies.py` provides transactional sessions
- Slugs auto-generated from names with collision handling
- File uploads validated by type and size (configurable via env)
- All timestamps are timezone-aware (UTC)
