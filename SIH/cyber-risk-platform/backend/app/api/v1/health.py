"""
Health check endpoint.

Provides application health status including database connectivity.
"""

import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    database: str = "unknown"
    version: str = "0.1.0"


@router.get("", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Application health check.

    Returns the current health status of the platform including database connectivity.
    """
    db_status = "unknown"
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.warning("Database health check failed: %s", e)
        db_status = "unhealthy"

    overall = "healthy" if db_status == "healthy" else "degraded"

    return HealthResponse(status=overall, database=db_status, version="0.1.0")

