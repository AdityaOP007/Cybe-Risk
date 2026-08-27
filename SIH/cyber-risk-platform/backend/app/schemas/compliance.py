import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# ----------------- Framework -----------------

class ComplianceFrameworkBase(BaseModel):
    name: str
    version: Optional[str] = None
    jurisdiction: Optional[str] = None
    effective_date: Optional[datetime] = None
    source_reference: Optional[str] = None
    status: str = "active"

class ComplianceFrameworkRead(ComplianceFrameworkBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Requirement -----------------

class ComplianceRequirementBase(BaseModel):
    requirement_id: str
    parent_requirement_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    applicability: Optional[str] = None
    requirement_type: Optional[str] = None
    source_reference: Optional[str] = None
    effective_date: Optional[datetime] = None
    status: str = "active"

class ComplianceRequirementRead(ComplianceRequirementBase):
    id: uuid.UUID
    framework_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Applicability -----------------

class ComplianceApplicabilityRequest(BaseModel):
    requirement_id: uuid.UUID
    status: str = Field(..., description="applicable, not_applicable, requires_review")
    rationale: Optional[str] = None

class ComplianceApplicabilityRead(ComplianceApplicabilityRequest):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Mapping -----------------

class ComplianceControlMappingRead(BaseModel):
    id: uuid.UUID
    framework_id: uuid.UUID
    requirement_id: uuid.UUID
    control_id: uuid.UUID
    mapping_type: str
    coverage_percentage: Optional[float] = None
    confidence: Optional[float] = None
    rationale: Optional[str] = None
    source: Optional[str] = None
    
    class Config:
        from_attributes = True

# ----------------- Evidence -----------------

class ComplianceEvidenceBase(BaseModel):
    control_id: uuid.UUID
    requirement_id: Optional[uuid.UUID] = None
    evidence_type: str
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    source_reference: Optional[str] = None
    collected_at: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: str = "valid"
    confidence: Optional[float] = None

class ComplianceEvidenceCreate(ComplianceEvidenceBase):
    pass

class ComplianceEvidenceRead(ComplianceEvidenceBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Assessment -----------------

class ComplianceAssessmentRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    framework_id: uuid.UUID
    requirement_id: uuid.UUID
    status: str
    coverage: Optional[float] = None
    confidence: Optional[float] = None
    evidence_completeness: Optional[float] = None
    control_effectiveness: Optional[float] = None
    risk_level: Optional[str] = None
    assessment_date: datetime
    assessor: Optional[str] = None
    notes: Optional[str] = None
    calculation_version: Optional[str] = None
    
    class Config:
        from_attributes = True

# ----------------- Gaps -----------------

class ComplianceGapRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    framework_id: uuid.UUID
    requirement_id: uuid.UUID
    control_id: Optional[uuid.UUID] = None
    asset_id: Optional[uuid.UUID] = None
    gap_type: str
    severity: str
    risk_score: Optional[float] = None
    financial_exposure: Optional[float] = None
    description: str
    evidence_gap: Optional[str] = None
    recommendation_id: Optional[uuid.UUID] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Exceptions -----------------

class ComplianceExceptionBase(BaseModel):
    requirement_id: uuid.UUID
    control_id: Optional[uuid.UUID] = None
    reason: str
    business_justification: str
    expires_at: Optional[datetime] = None

class ComplianceExceptionCreate(ComplianceExceptionBase):
    pass

class ComplianceExceptionRead(ComplianceExceptionBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Framework Summary -----------------

class FrameworkAssessmentSummary(BaseModel):
    framework_id: uuid.UUID
    framework_name: str
    framework_version: Optional[str] = None
    applicable_requirements: int
    compliant: int
    partially_compliant: int
    non_compliant: int
    insufficient_evidence: int
    not_assessed: int
    not_applicable: int
    exceptions: int
    coverage_percentage: float
    evidence_coverage: float
    overall_confidence: float
    last_assessed: Optional[datetime] = None
