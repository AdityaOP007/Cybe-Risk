"""
Health check endpoint.

Provides a basic application health status. Structured so future modules
can extend it with dependency checks (database, AI service, etc.).
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    # Future fields can be added here without breaking existing clients:
    # database: str | None = None
    # ai_service: str | None = None
    # data_ingestion: str | None = None


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Application health check.

    Returns the current health status of the platform.
    Future modules will extend this to check database connectivity,
    AI service availability, and other dependencies.
    """
    return HealthResponse(status="healthy")
