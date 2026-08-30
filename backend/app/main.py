"""FastAPI application factory and main entrypoint."""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import api_router
from app.api.routes.health import health_check
from app.core.config import Settings, get_settings
from app.core.logging import get_logger, setup_logging
from app.core.security import generate_request_id
from app.schemas.base import APIError, APIResponse

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    settings: Settings = getattr(app.state, "settings", None) or get_settings()
    setup_logging(
        level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        enable_pii_masking=settings.ENABLE_PII_MASKING,
    )
    logger.info("Initializing %s (v%s) in %s mode", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)

    # Initialize database tables
    try:
        import app.models  # noqa: F401
        from app.db.base import Base
        from app.db.session import async_engine
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified/created successfully.")
    except Exception as exc:
        logger.warning("Could not auto-create database tables (fallback mode): %s", exc)

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


def create_app(settings: Settings | None = None) -> FastAPI:
    """FastAPI application factory."""
    app_settings = settings or get_settings()

    app = FastAPI(
        title=app_settings.APP_NAME,
        version=app_settings.APP_VERSION,
        description="AI-powered Indian Income Tax Return analysis and assistance platform.",
        docs_url="/docs" if app_settings.DEBUG or app_settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if app_settings.DEBUG or app_settings.APP_ENV != "production" else None,
        lifespan=lifespan,
    )
    app.state.settings = app_settings

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Telemetry Middleware
    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-MS"] = str(process_time_ms)

        # Structured request logging
        logger.info(
            "%s %s -> %s (%sms)",
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
            extra={"request_id": request_id},
        )
        return response

    # Custom Domain Exception Handler
    from app.core.exceptions import AppException

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "req_unknown")
        logger.warning(
            "Application error [%s]: %s",
            exc.code,
            exc.message,
            extra={"request_id": request_id, "details": exc.details},
        )
        error_response = APIResponse(
            success=False,
            data=None,
            error=APIError(
                code=exc.code,
                message=exc.message,
                details=exc.details,
            ),
            request_id=request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
            headers={"X-Request-ID": request_id},
        )

    # Global Exception Handlers for both FastAPI & Starlette HTTPExceptions
    @app.exception_handler(StarletteHTTPException)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException | StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "req_unknown")
        error_response = APIResponse(
            success=False,
            data=None,
            error=APIError(
                code=f"HTTP_{exc.status_code}",
                message=str(exc.detail),
            ),
            request_id=request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "req_unknown")
        logger.exception("Unhandled server exception: %s", str(exc), extra={"request_id": request_id})

        error_response = APIResponse(
            success=False,
            data=None,
            error=APIError(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal error occurred. Please try again later.",
            ),
            request_id=request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
            headers={"X-Request-ID": request_id},
        )

    # Root Health Check (GET /health)
    app.add_api_route("/health", health_check, methods=["GET"], tags=["Health"], summary="Root Health Check")

    # API v1 Router (GET /api/v1/health etc.)
    app.include_router(api_router, prefix=app_settings.API_V1_STR)

    # Mount interactive Nuxt 3 frontend UI
    from pathlib import Path
    from starlette.types import Scope, Receive, Send
    from fastapi.staticfiles import StaticFiles

    class SPAStaticFiles(StaticFiles):
        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            if scope.get("path", "").startswith("/api/"):
                raise StarletteHTTPException(status_code=404, detail="Not Found")
            await super().__call__(scope, receive, send)

    candidate_frontend_paths = [
        Path(__file__).resolve().parent.parent.parent / "frontend" / ".output" / "public",  # Nuxt 3 local build
        Path("/app/frontend/.output/public"),                                              # Nuxt 3 docker build
        Path(__file__).resolve().parent.parent.parent / "frontend",                         # Local dev static
        Path("/app/frontend"),                                                             # Docker mounted /app/frontend
        Path("/frontend"),                                                                 # Docker root
        Path("frontend"),                                                                  # Cwd
    ]

    frontend_dir = next((p for p in candidate_frontend_paths if p.exists() and (p / "index.html").exists()), None)
    if frontend_dir:
        app.mount("/", SPAStaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app


# Default application instance for ASGI servers (Uvicorn)
app = create_app()
