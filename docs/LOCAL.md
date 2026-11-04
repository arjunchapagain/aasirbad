# Run Aasirbad locally

Requirements: Python 3.11+, Node 20+, PostgreSQL 16 (Redis only if `TASK_MODE=celery`).

```bash
# 1. Database
createdb aasirbad   # user aasirbad / password aasirbad_secret (or edit backend/.env)

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example .env
alembic upgrade head          # run migrations BEFORE the first start
uvicorn app.main:app --reload # http://localhost:8000/docs

# 3. Frontend (new terminal)
cd frontend && npm ci && npm run dev   # http://localhost:3000
```

Use it: register, create a voice (tick the consent box), copy the recording link, open it,
record at least 5 clips, press Train on the dashboard, then Generate Speech.

## Real voice cloning
Default `TTS_PROVIDER=demo` produces placeholder tones so the app runs without keys.
For real cloning set `TTS_PROVIDER=elevenlabs` and `ELEVENLABS_API_KEY=...` in `backend/.env`.
Free-tier limits: 3 voices per user, 5,000 characters of synthesis per month.

## Tests
```bash
scripts/check.sh                       # backend tests + alembic head check + frontend tsc
python scripts/e2e.py                  # API end-to-end against a running backend
```
`scripts/ui-e2e.js` is a Playwright browser flow (needs a speech WAV for the fake microphone).
