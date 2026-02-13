# VoiceForge — Voice Cloning Platform

A professional voice cloning platform that lets you capture someone's voice through guided recordings and then synthesize speech in that voice using Tortoise TTS.

## How It Works

1. **Create a Voice Profile** — Register an account, create a named voice profile, and generate a shareable recording link.
2. **Record Voice Samples** — Send the link to the target speaker. They record 20 curated prompts (pangrams, emotions, conversational phrases) directly in the browser.
3. **Train the Voice Model** — Trigger training from the dashboard. The system extracts conditioning latents from the recordings using Tortoise TTS.
4. **Synthesize Speech** — Enter any text and generate speech in the cloned voice with adjustable quality presets.

---

## Architecture

```
┌────────────┐        ┌──────────────┐        ┌───────────────┐
│  Next.js   │  REST  │   FastAPI    │  Celery │  GPU Worker   │
│  Frontend  │◄──────►│   Backend    │◄───────►│  (Tortoise)   │
└────────────┘        └──────┬───────┘        └───────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌──────────┐
        │ Postgres │  │   Redis   │  │  AWS S3  │
        │   (DB)   │  │ (Broker)  │  │ (Storage)│
        └──────────┘  └───────────┘  └──────────┘
```

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14 (App Router), React 18, Tailwind CSS, Framer Motion |
| Backend API | FastAPI, Python 3.10+, SQLAlchemy 2.0 (async), Pydantic v2 |
| Voice Engine | Tortoise TTS, PyTorch, librosa, noisereduce |
| Task Queue | Celery with Redis broker |
| Database | PostgreSQL 16 (asyncpg driver) |
| Storage | AWS S3 (audio files + trained models) |
| Auth | JWT (access + refresh tokens), bcrypt |
| Deployment | Docker Compose, NVIDIA CUDA workers |

---

## Project Structure

```
aasirbad/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Security, audio processing
│   │   ├── voice_engine/    # Preprocessor, Trainer, Synthesizer
│   │   ├── workers/         # Celery tasks
│   │   ├── config.py        # Settings (env-based)
│   │   ├── database.py      # Async DB setup
│   │   └── main.py          # FastAPI app + WebSocket
│   ├── alembic/             # DB migrations
│   ├── tests/               # pytest test suite
│   ├── Dockerfile
│   ├── Dockerfile.worker    # GPU-enabled worker image
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages (App Router)
│   │   ├── hooks/           # useAudioRecorder, useWebSocket
│   │   ├── lib/             # API client, audio utilities
│   │   └── types/           # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 16
- Redis 7
- AWS S3 bucket (or compatible object storage)
- NVIDIA GPU with CUDA 12.1 (for training; CPU fallback available)

### 1. Clone & Configure

```bash
git clone <repo-url> && cd aasirbad
cp .env.example .env
# Edit .env with your database, Redis, S3, and JWT settings
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start Celery Workers

```bash
# CPU worker (preprocessing)
celery -A app.workers.celery_app worker -Q cpu -c 4 --loglevel=info

# GPU worker (training) — requires NVIDIA GPU
celery -A app.workers.celery_app worker -Q gpu -c 1 -P solo --loglevel=info
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### 5. Docker Compose (Full Stack)

```bash
# Standard deployment (CPU workers only)
docker compose up -d

# With GPU training worker
docker compose --profile gpu up -d

# With Flower monitoring dashboard
docker compose --profile monitoring up -d
```

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login, receive tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

### Voice Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/voice-profiles` | Create profile |
| GET | `/api/v1/voice-profiles` | List profiles (paginated) |
| GET | `/api/v1/voice-profiles/{id}` | Get profile details |
| DELETE | `/api/v1/voice-profiles/{id}` | Delete profile |
| GET | `/api/v1/voice-profiles/{id}/link` | Get shareable recording link |
| POST | `/api/v1/voice-profiles/{id}/train` | Trigger voice training |
| GET | `/api/v1/voice-profiles/record/{token}` | Get recording session (public) |

### Recordings

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/recordings/{token}/upload` | Upload audio recording (public) |
| GET | `/api/v1/recordings/profile/{id}` | List recordings for a profile |

### Synthesis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/synthesis/generate` | Generate speech from text |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://host/ws/training/{profile_id}` | Real-time training progress |

---

## Voice Quality Presets

| Preset | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| `ultra_fast` | ~2s | Low | Quick previews |
| `fast` | ~8s | Medium | Drafts |
| `standard` | ~30s | High | General use |
| `high_quality` | ~2min | Best | Final output |

---

## Recording Prompts

The system uses 20 curated prompts designed to capture the full vocal range:

- **Pangrams** — Cover all phonemes ("The quick brown fox...")
- **Emotional range** — Happy, sad, serious, excited tones
- **Conversational** — Natural speaking patterns
- **Numbers & dates** — Precise pronunciation
- **Questions** — Intonation patterns

### Audio Quality Thresholds

| Metric | Threshold |
|--------|-----------|
| Signal-to-Noise Ratio | ≥ 10 dB |
| RMS Level | ≥ -40 dB |
| Silence Ratio | ≤ 50% |
| Clipping | Not detected |

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://...` |
| `REDIS_HOST` | Redis server | `localhost` |
| `AWS_S3_BUCKET_AUDIO` | Audio storage bucket | `voiceforge-audio` |
| `AWS_S3_BUCKET_MODELS` | Model storage bucket | `voiceforge-models` |
| `JWT_SECRET_KEY` | JWT signing key | (generate a random one) |
| `VOICE_ENGINE_DEVICE` | `cuda` or `cpu` | `cpu` |

---

## Testing

```bash
cd backend
pip install -e ".[dev]"

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

---

## Deployment Notes

- **GPU Workers**: Use the `Dockerfile.worker` image on GPU-enabled instances. Training requires ~4 GB VRAM minimum.
- **S3 Permissions**: The API and workers need `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, and `s3:ListBucket`.
- **Scaling**: CPU workers can scale horizontally. GPU workers should run with concurrency=1 and solo pool.
- **Monitoring**: Enable the `monitoring` Docker Compose profile to access Flower at `http://localhost:5555`.
- **Security**: Always set `ENVIRONMENT=production` in production to enable HTTPS enforcement and trusted host middleware.

---

## License

Private — All rights reserved.
