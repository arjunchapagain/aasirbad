# Aasirbad — voice cloning platform

Next.js 14 frontend (`frontend/`) + FastAPI backend (`backend/`), Postgres, Redis/Celery. Not deployed anywhere (local only); no deploy automation.

## Commands
- Backend tests: `cd backend && DB_BACKEND=sqlite pytest -q`
- Migrations: `cd backend && alembic upgrade head` (must stay a SINGLE head: check `alembic heads`)
- Frontend check: `cd frontend && npx tsc --noEmit && npm run build`
- API e2e (needs running backend): `python scripts/e2e.py`; run guide: `docs/LOCAL.md`
- Full check before commit: `scripts/check.sh` (also runs as git pre-commit hook; enable with `git config core.hooksPath .githooks`)

## Rules
- Postgres is the real DB; SQLite is for tests only. Migrations are Postgres-only SQL, test them on Postgres.
- Enums are stored as lowercase values (`values_callable`), never names.
- New migration = new file chained to the current head. Never edit applied migrations; never branch.
- Secrets only via env vars (see `.env.example`). Never commit `.env*` with real values.
- TTS runs through a hosted API behind `backend/app/voice_engine/` (no local GPU). Keep it behind one interface.
- English only for now. Don't build i18n yet; keep UI strings easy to extract later (see `docs/PLAN.md` milestone 3, deferred).

## Working style (save tokens)
- One feature per session/branch. State a 3-5 line plan, then implement.
- Read only the files you need; use Grep before Read. Don't read `docs/archive/` or lockfiles.
- Don't re-run the full build to check a small change; run the narrowest test.
- Keep replies short: what changed, what was verified, what's next.

Plan and open decisions: `docs/PLAN.md`
