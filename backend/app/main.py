import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import configure_logging, settings
from app.routers import auth, health, ingest, sources, tools

# ── configure logging FIRST before any other logger is used ──────────────────
configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "startup: Persona backend starting | is_prod=%s | log_level=%s",
        settings.is_prod,
        settings.log_level,
    )
    yield
    logger.info("shutdown: Persona backend stopping")


app = FastAPI(title="AI Call Backend", lifespan=lifespan)


# ── Middleware ─────────────────────────────────────────────────────────────────

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request and its response status + duration."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]   # short id, easy to spot in logs
        request.state.request_id = request_id
        start = time.perf_counter()

        logger.info(
            "→ %s %s | req_id=%s | client=%s",
            request.method,
            request.url.path,
            request_id,
            request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
        except Exception as exc:                         # pragma: no cover
            elapsed = (time.perf_counter() - start) * 1000
            logger.exception(
                "✗ %s %s | req_id=%s | UNHANDLED ERROR after %.1f ms: %s",
                request.method,
                request.url.path,
                request_id,
                elapsed,
                exc,
            )
            raise

        elapsed = (time.perf_counter() - start) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            level,
            "← %s %s | req_id=%s | status=%d | %.1f ms",
            request.method,
            request.url.path,
            request_id,
            response.status_code,
            elapsed,
        )
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r".*",  # allow all origins (frontend URLs)
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    # x-vapi-secret must be listed explicitly — wildcard headers break credentialed CORS
    allow_headers=["Content-Type", "x-vapi-secret"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    req_id = getattr(request.state, "request_id", "?")
    logger.warning(
        "HTTP %d | req_id=%s | path=%s | detail=%s",
        exc.status_code,
        req_id,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


app.include_router(auth.router)
app.include_router(sources.router)
app.include_router(ingest.router)
app.include_router(tools.router)
app.include_router(health.router)
