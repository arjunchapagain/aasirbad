# Copilot & AI Agent Instructions for VoiceForge (Aasirbad)

## Project Overview
- **VoiceForge** is a full-stack voice cloning platform: users record prompts, models are trained, and speech is synthesized in the cloned voice.
- **Architecture:**
  - **Frontend:** Next.js (App Router), React, Tailwind CSS
  - **Backend:** FastAPI (Python), async SQLAlchemy, Celery workers
  - **Voice Engine:** Tortoise TTS, PyTorch
  - **Data:** PostgreSQL (async), Redis (broker), AWS S3 (audio/models)
  - **Deployment:** Docker Compose, GPU/CPU workers, Nginx

## Key Code Structure
- `backend/app/api/v1/` — REST endpoints (auth, voice_profiles, recordings, synthesis)
- `backend/app/models/` — SQLAlchemy models (async, enums for status fields)
- `backend/app/schemas/` — Pydantic schemas (v2)
- `backend/app/services/` — Business logic (profile creation, training, etc.)
- `backend/app/voice_engine/` — Preprocessing, training, synthesis logic
- `backend/app/workers/` — Celery tasks (CPU/GPU separation)
- `frontend/src/app/` — Next.js pages (App Router)
- `frontend/src/lib/` — API client, audio utils

## Essential Workflows
- **Local Dev:**
  - Backend: `uvicorn app.main:app --reload`
  - Frontend: `npm run dev`
  - Migrations: `alembic upgrade head` (see Docker caveats below)
  - Tests: `pytest -v` (backend)
- **Docker Compose:**
  - `docker compose up -d` (CPU stack)
  - `docker compose --profile gpu up -d` (GPU worker)
  - **Volume mount:** `./backend/app:/app` for correct Python imports
- **Celery Workers:**
  - CPU: `celery -A app.workers.celery_app worker -Q cpu -c 4`
  - GPU: `celery -A app.workers.celery_app worker -Q gpu -c 1 -P solo`
- **Monitoring:**
  - Flower dashboard: `docker compose --profile monitoring up -d` (http://localhost:5555)

## Project-Specific Conventions
- **Enum Status Fields:**
  - All status enums (e.g., `ProfileStatus`) use lowercase values in Python and the DB (e.g., `'pending'`, `'ready'`).
  - If you see DB errors about enum values, check for case mismatches.
- **Async Everywhere:**
  - All DB and API code is async (use `asyncpg`, `async SQLAlchemy`).
- **Separation of Concerns:**
  - API = routing only; business logic in `services/`; DB models in `models/`; schemas in `schemas/`.
- **Voice Engine:**
  - Training and synthesis logic is in `voice_engine/` and dispatched via Celery workers.
- **Frontend API Calls:**
  - Use `frontend/src/lib/api.ts` for all backend communication.

## Integration & External Dependencies
- **AWS S3:** Used for audio and model storage. Credentials in `.env`.
- **Redis:** Used as Celery broker and for caching.
- **PostgreSQL:** All models use async SQLAlchemy; migrations via Alembic.
- **Nginx:** Serves frontend, proxies API, handles SSL (see `deploy/nginx/`).

## Troubleshooting & Gotchas
- **Alembic in Docker:**
  - Ensure `PYTHONPATH=/app` and volume mount is `./backend/app:/app` for migrations to work.
  - If you see `ModuleNotFoundError: No module named 'app.config'`, check Docker volume and PYTHONPATH.
- **Celery GPU Worker:**
  - Must run with `-P solo` and concurrency=1 for GPU safety.
- **JWT Auth:**
  - All endpoints except `/auth/*` require JWT Bearer tokens.
- **Testing:**
  - Use `pytest` in `backend/` for backend tests. Coverage: `pytest --cov=app --cov-report=html`.

## Example: Creating a Voice Profile
- POST `/api/v1/voice-profiles` with `{ name, description }` (auth required)
- Backend creates profile with status `'pending'`, generates recording token
- User records prompts via shareable link
- Training is triggered via `/api/v1/voice-profiles/{id}/train`

---

For more, see `README.md` and `backend/README.md`. If you encounter ambiguous patterns, review the `services/` and `voice_engine/` directories for canonical logic.
