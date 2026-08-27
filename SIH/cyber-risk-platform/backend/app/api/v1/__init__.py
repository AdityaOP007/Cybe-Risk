"""API v1 router — aggregates all v1 endpoint modules."""

from fastapi import APIRouter

from app.api.v1 import health
from app.api.v1 import organizations
from app.api.v1 import assets
from app.api.v1 import vulnerabilities
from app.api.v1 import controls
from app.api.v1 import telemetry
from app.api.v1 import threat_intel
from app.api.v1 import risk
from app.api.v1 import financial_risk
from app.api.v1 import predictions
from app.api.v1 import recommendations
from app.api.v1 import optimization
from app.api.v1 import compliance

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["Vulnerabilities"])
api_router.include_router(controls.router, prefix="/controls", tags=["Security Controls"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Security Telemetry"])
api_router.include_router(threat_intel.router, tags=["Threat Intelligence"])
api_router.include_router(risk.router)
api_router.include_router(financial_risk.router)
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["Optimization"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])
