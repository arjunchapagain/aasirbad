"""
VoiceForge - Main FastAPI Application.

Professional voice cloning platform powered by Tortoise TTS.
"""

import json
import logging
import secrets
import time
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import structlog
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_router
from app.config import get_settings
from app.database import close_db, init_db, wait_for_db
from app.utils.security import decode_access_token

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
        logging.getLevelName(settings.log_level),
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


# ── Application Lifecycle ────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting Aasirbad API", env=settings.app_env)

    # Refuse to start in production with default secrets
    if settings.app_env == "production":
        if settings.secret_key in ("change-me-in-production", ""):
            raise RuntimeError("SECRET_KEY must be set in production")
        if settings.jwt_secret_key in ("jwt-secret-change-in-production", ""):
            raise RuntimeError("JWT_SECRET_KEY must be set in production")

    # Wait for database to be available (handles Render provisioning delay)
    db_ready = await wait_for_db(retries=20, delay=5.0)
    if not db_ready:
        logger.error("Could not connect to database — starting anyway")

    if settings.app_env == "development" and db_ready:
        try:
            await init_db()
            logger.info("Database tables created (development mode)")
        except Exception as exc:
            logger.error("Failed to create tables (non-fatal)", error=str(exc))

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
    logger.info("Shutting down Aasirbad API")
    await close_db()


# ── Create Application ───────────────────────────────────────────────────────

app = FastAPI(
    title="Aasirbad API",
    description=(
        "Preserve your family's voice forever. "
        "Record voice samples, train custom voice models, "
        "and generate speech in your loved one's voice."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────────────


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add X-Request-ID header for tracing (iOS debugging, support tickets)."""
    request_id = request.headers.get("X-Request-ID") or secrets.token_hex(8)
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add standard security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.app_env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# Upload body size limit (10 MB)
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    """Reject requests with bodies larger than MAX_BODY_SIZE."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large. Maximum is 10 MB."},
        )
    return await call_next(request)


# Simple in-memory rate limiter (per-IP, per-endpoint)
_rate_limit_store: dict[str, list[float]] = {}
RATE_LIMITS = {
    "/api/v1/auth/login": (5, 60),        # 5 attempts per 60 seconds
    "/api/v1/auth/register": (3, 60),      # 3 registrations per 60 seconds
}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Rate limit sensitive endpoints by IP."""
    path = request.url.path
    limit_config = RATE_LIMITS.get(path)
    if limit_config and request.method == "POST":
        max_requests, window = limit_config
        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{path}"
        now = time.time()

        # Clean old entries & check
        hits = _rate_limit_store.get(key, [])
        hits = [t for t in hits if now - t < window]
        if len(hits) >= max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(window)},
            )
        hits.append(now)
        _rate_limit_store[key] = hits

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

if settings.app_env == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.onrender.com", "*.aasirbad.com", "aasirbad.com"],
    )


# ── Global Exception Handler ─────────────────────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions - never leak stack traces to clients."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Unhandled exception",
        request_id=request_id,
        path=request.url.path,
        error=str(exc),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api")


# ── Local File Serving (with path traversal protection) ──────────────────────

if settings.storage_backend == "local":
    from pathlib import Path as _Path

    from fastapi.responses import FileResponse

    @app.get("/api/v1/files/{file_path:path}", tags=["Files"])
    async def serve_local_file(file_path: str):
        """Serve locally stored audio/model files. Path traversal protected."""
        base = _Path(settings.local_storage_dir).resolve()
        # Try audio dir first, then models dir
        for subdir in ("audio", "models"):
            full_path = (base / subdir / file_path).resolve()
            # Prevent path traversal: resolved path MUST be inside base
            if not full_path.is_relative_to(base):
                raise HTTPException(status_code=403, detail="Access denied")
            if full_path.exists() and full_path.is_file():
                return FileResponse(full_path, media_type="audio/wav")
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for load balancer."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


# ── WebSocket for Training Status (with token auth) ─────────────────────────

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
            dead: list[WebSocket] = []
            for connection in self.active_connections[profile_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead.append(connection)
            # Clean up dead connections
            for ws in dead:
                self.active_connections[profile_id].remove(ws)


manager = ConnectionManager()


@app.websocket("/ws/training/{profile_id}")
async def training_status_websocket(websocket: WebSocket, profile_id: str):
    """
    WebSocket endpoint for real-time training status updates.
    Requires ?token=<jwt> query param for authentication.
    """
    # Authenticate via query param
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket, profile_id)

    # Subscribe to Redis channel
    try:
        redis = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password or None,
        )
    except Exception:
        await websocket.close(code=1011, reason="Service unavailable")
        return

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
