"""
VoiceForge - Main FastAPI Application.

Professional voice cloning platform powered by Tortoise TTS.
"""

import json
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import router as api_router
from app.config import get_settings
from app.database import close_db, init_db

settings = get_settings()

# ── Logging Setup ────────────────────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.getLevelName(settings.log_level)
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


# ── Application Lifecycle ────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting VoiceForge API", env=settings.app_env)

    if settings.app_env == "development":
        await init_db()
        logger.info("Database tables created (development mode)")

    # Sentry integration
    if settings.sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
            environment=settings.app_env,
        )
        logger.info("Sentry initialized")

    yield

    # Shutdown
    logger.info("Shutting down VoiceForge API")
    await close_db()


# ── Create Application ───────────────────────────────────────────────────────

app = FastAPI(
    title="VoiceForge API",
    description=(
        "Professional voice cloning platform. "
        "Record voice samples, train custom voice models, "
        "and generate speech in any cloned voice."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.app_env == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.voiceforge.app", "voiceforge.app"],
    )


# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api")


# ── Local File Serving (dev only) ────────────────────────────────────────────

if settings.storage_backend == "local":
    from pathlib import Path as _Path
    from fastapi.responses import FileResponse

    @app.get("/api/v1/files/{file_path:path}", tags=["Files"])
    async def serve_local_file(file_path: str):
        """Serve locally stored audio/model files during development."""
        base = _Path(settings.local_storage_dir).resolve()
        # Try audio dir first, then models dir
        for subdir in ("audio", "models"):
            full_path = base / subdir / file_path
            if full_path.exists() and full_path.is_file():
                return FileResponse(full_path, media_type="audio/wav")
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for load balancer."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


# ── WebSocket for Training Status ────────────────────────────────────────────

class ConnectionManager:
    """Manages WebSocket connections for real-time training updates."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, profile_id: str):
        await websocket.accept()
        if profile_id not in self.active_connections:
            self.active_connections[profile_id] = []
        self.active_connections[profile_id].append(websocket)

    def disconnect(self, websocket: WebSocket, profile_id: str):
        if profile_id in self.active_connections:
            self.active_connections[profile_id].remove(websocket)
            if not self.active_connections[profile_id]:
                del self.active_connections[profile_id]

    async def broadcast(self, profile_id: str, message: dict):
        if profile_id in self.active_connections:
            for connection in self.active_connections[profile_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


@app.websocket("/ws/training/{profile_id}")
async def training_status_websocket(websocket: WebSocket, profile_id: str):
    """
    WebSocket endpoint for real-time training status updates.
    
    Subscribes to Redis Pub/Sub channel for the given profile
    and forwards messages to the connected client.
    """
    await manager.connect(websocket, profile_id)

    # Subscribe to Redis channel
    redis = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password or None,
    )
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"training:{profile_id}")

    try:
        # Forward Redis messages to WebSocket
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)

                # Close if training is complete or failed
                if data.get("status") in ("ready", "failed"):
                    break
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(f"training:{profile_id}")
        await redis.close()
        manager.disconnect(websocket, profile_id)
