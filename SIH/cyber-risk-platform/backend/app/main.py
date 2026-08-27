"""
Cyber Risk Platform — FastAPI Application Entry Point.

Configures the FastAPI application, CORS middleware, routers,
and global exception handling.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Initialize logging before anything else
setup_logging(level="DEBUG" if settings.DEBUG else "INFO")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — replaces deprecated on_event("startup") / on_event("shutdown")
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup and shutdown logic."""
    logger.info(
        "Starting %s (env=%s, debug=%s)",
        settings.APP_NAME,
        settings.APP_ENV,
        settings.DEBUG,
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered cyber risk quantification and decision intelligence platform. "
        "Quantifies cyber risk in financial terms by combining security telemetry, "
        "asset criticality, vulnerabilities, threat intelligence, and AI/ML prediction."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — restrict to configured frontend URL in production
# ---------------------------------------------------------------------------
cors_origins: list[str] = [settings.FRONTEND_URL]

if settings.DEBUG:
    # In development, also allow common local origins
    cors_origins.extend(
        [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]
    )
    # Deduplicate while preserving order
    cors_origins = list(dict.fromkeys(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix="/api")


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint — confirms the API is running."""
    return {
        "name": settings.APP_NAME,
        "status": "running",
    }


# ---------------------------------------------------------------------------
# Global exception handler — prevents leaking internals to clients
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )
