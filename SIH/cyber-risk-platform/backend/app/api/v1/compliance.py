from typing import List, Dict, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.compliance import (
    ComplianceFramework, ComplianceRequirement, ComplianceControlMapping,
    ComplianceEvidence, ComplianceGap, ComplianceAssessment
)
from app.schemas.compliance import (
    ComplianceFrameworkRead, ComplianceRequirementRead,
    ComplianceControlMappingRead, ComplianceEvidenceRead,
    ComplianceGapRead, FrameworkAssessmentSummary, ComplianceAssessmentRead
)
from app.services.compliance.engine import ComplianceEngine

router = APIRouter()

@router.get("/frameworks", response_model=List[ComplianceFrameworkRead])
def get_frameworks(db: Session = Depends(get_db)):
    return db.scalars(select(ComplianceFramework)).all()

@router.get("/frameworks/{framework_id}/requirements", response_model=List[ComplianceRequirementRead])
def get_framework_requirements(framework_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.scalars(
        select(ComplianceRequirement).where(ComplianceRequirement.framework_id == framework_id)
    ).all()

@router.post("/frameworks/{framework_id}/assess", response_model=FrameworkAssessmentSummary)
def assess_framework(
    framework_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = ComplianceEngine(db, current_user.organization_id)
    return engine.assess_framework(framework_id)

@router.get("/frameworks/{framework_id}/summary", response_model=FrameworkAssessmentSummary)
def get_framework_summary(
    framework_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Try to calculate an on-the-fly summary if data is present
    engine = ComplianceEngine(db, current_user.organization_id)
    return engine.assess_framework(framework_id)

@router.get("/gaps", response_model=List[ComplianceGapRead])
def get_compliance_gaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.scalars(
        select(ComplianceGap)
        .where(ComplianceGap.organization_id == current_user.organization_id)
        .order_by(desc(ComplianceGap.created_at))
    ).all()

@router.get("/crosswalk/control/{control_id}")
def get_control_crosswalk(
    control_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = ComplianceEngine(db, current_user.organization_id)
    return engine.get_crosswalk(control_id)
