"""API v1 router — aggregates all v1 endpoint modules."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router

router = APIRouter()
router.include_router(health_router, tags=["Health"])
