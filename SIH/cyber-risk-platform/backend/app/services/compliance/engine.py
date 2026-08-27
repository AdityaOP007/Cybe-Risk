import uuid
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.compliance import (
    ComplianceFramework, ComplianceRequirement, ComplianceApplicability,
    ComplianceControlMapping, ComplianceEvidence, ComplianceAssessment,
    ComplianceGap, ComplianceException
)
from app.models.control import SecurityControl
from app.models.risk import RiskScore
from app.schemas.compliance import FrameworkAssessmentSummary
from app.models.mixins import get_utc_now

class ComplianceEngine:
    def __init__(self, db: Session, organization_id: uuid.UUID):
        self.db = db
        self.org_id = organization_id

    def assess_framework(self, framework_id: uuid.UUID) -> FrameworkAssessmentSummary:
        """
        Assess an entire framework and persist the results.
        Returns the summary of the assessment.
        """
        framework = self.db.query(ComplianceFramework).filter(ComplianceFramework.id == framework_id).first()
        if not framework:
            raise ValueError(f"Framework {framework_id} not found")

        requirements = self.db.query(ComplianceRequirement).filter(
            ComplianceRequirement.framework_id == framework_id
        ).all()

        # Load contexts
        applicabilities = self._load_applicability(framework_id)
        mappings = self._load_mappings(framework_id)
        controls = self._load_controls()
        evidence = self._load_evidence()
        exceptions = self._load_exceptions(framework_id)
        
        now = get_utc_now()
        calculation_version = "1.0"
        
        # Clear current assessments and gaps for this framework to generate a fresh snapshot
        # (In a real system, you might append history, but here we overwrite current state)
        self.db.query(ComplianceAssessment).filter(
            ComplianceAssessment.organization_id == self.org_id,
            ComplianceAssessment.framework_id == framework_id
        ).delete()
        
        self.db.query(ComplianceGap).filter(
            ComplianceGap.organization_id == self.org_id,
            ComplianceGap.framework_id == framework_id,
            ComplianceGap.status == "open"
        ).delete()
        
        assessments_to_add = []
        gaps_to_add = []

        # Metrics for summary
        metrics = {
            "applicable": 0, "compliant": 0, "partial": 0, 
            "non_compliant": 0, "insufficient_evidence": 0, 
            "not_assessed": 0, "not_applicable": 0, "exceptions": 0,
            "total_confidence": 0.0, "total_evidence_completeness": 0.0
        }

        for req in requirements:
            # 1. Applicability
            app_status = applicabilities.get(req.id, req.applicability or "applicable")
            if app_status == "not_applicable":
                metrics["not_applicable"] += 1
                assessments_to_add.append(
                    ComplianceAssessment(
                        organization_id=self.org_id, framework_id=framework_id, requirement_id=req.id,
                        status="not_applicable", assessment_date=now, calculation_version=calculation_version
                    )
                )
                continue
                
            metrics["applicable"] += 1

            # 2. Exceptions
            exception = exceptions.get(req.id)
            if exception and exception.expires_at and exception.expires_at > now and exception.status == "approved":
                metrics["exceptions"] += 1
                assessments_to_add.append(
                    ComplianceAssessment(
                        organization_id=self.org_id, framework_id=framework_id, requirement_id=req.id,
                        status="exception", assessment_date=now, calculation_version=calculation_version,
                        notes=f"Approved exception: {exception.reason}"
                    )
                )
                continue

            # 3. Control Mapping & Evidence Evaluation
            req_mappings = mappings.get(req.id, [])
            if not req_mappings:
                status = "non_compliant"
                metrics["non_compliant"] += 1
                assessments_to_add.append(
                    ComplianceAssessment(
                        organization_id=self.org_id, framework_id=framework_id, requirement_id=req.id,
                        status=status, coverage=0.0, confidence=100.0, evidence_completeness=0.0,
                        control_effectiveness=0.0, assessment_date=now, calculation_version=calculation_version
                    )
                )
                gaps_to_add.append(
                    self._create_gap(framework_id, req.id, None, "missing_control", "high", "No controls mapped to this requirement.")
                )
                continue

            # Evaluate mapped controls
            total_coverage = 0.0
            total_effectiveness = 0.0
            total_evidence = 0.0
            best_status = "non_compliant"
            gap_details = []

            for mapping in req_mappings:
                control = controls.get(mapping.control_id)
                if not control:
                    continue
                
                # Check implementation
                if control.implementation_status in ["not_implemented", "planned", "unknown"]:
                    gap_details.append(f"Control '{control.name}' is not fully implemented.")
                    continue
                    
                # Check evidence
                ctrl_evidence = evidence.get(control.id, [])
                valid_evidence = [e for e in ctrl_evidence if e.status == "valid" and (not e.valid_until or e.valid_until > now)]
                
                if not valid_evidence:
                    best_status = "insufficient_evidence" if best_status == "non_compliant" else best_status
                    gap_details.append(f"Control '{control.name}' lacks valid evidence.")
                    continue
                    
                # Control is implemented and has evidence
                total_coverage += (mapping.coverage_percentage or 100.0)
                total_effectiveness += (control.effectiveness_percentage or 0.0)
                total_evidence += min(100.0, len(valid_evidence) * 25.0) # naive evidence scoring
                best_status = "compliant"
            
            # Finalize status based on aggregation
            final_status = best_status
            if best_status == "compliant" and total_effectiveness < 100.0: # simplistic check
                 final_status = "partially_compliant"
            elif best_status == "non_compliant":
                 final_status = "non_compliant"
                 
            # Edge case handling
            if final_status == "compliant":
                metrics["compliant"] += 1
            elif final_status == "partially_compliant":
                metrics["partial"] += 1
            elif final_status == "insufficient_evidence":
                metrics["insufficient_evidence"] += 1
            else:
                metrics["non_compliant"] += 1
                
            metrics["total_confidence"] += 80.0 # Default confidence
            metrics["total_evidence_completeness"] += min(100.0, total_evidence)
            
            assessments_to_add.append(
                ComplianceAssessment(
                    organization_id=self.org_id, framework_id=framework_id, requirement_id=req.id,
                    status=final_status, coverage=min(100.0, total_coverage), confidence=80.0, 
                    evidence_completeness=min(100.0, total_evidence),
                    control_effectiveness=min(100.0, total_effectiveness), assessment_date=now, calculation_version=calculation_version
                )
            )
            
            if final_status in ["partially_compliant", "non_compliant", "insufficient_evidence"]:
                gaps_to_add.append(
                    self._create_gap(framework_id, req.id, req_mappings[0].control_id if req_mappings else None, 
                                     final_status, "medium" if final_status == "partially_compliant" else "high",
                                     " | ".join(gap_details) or f"Requirement is {final_status}.")
                )

        # Commit assessments and gaps
        self.db.add_all(assessments_to_add)
        self.db.add_all(gaps_to_add)
        self.db.commit()

        # Calculate summary
        app_reqs = metrics["applicable"]
        summary = FrameworkAssessmentSummary(
            framework_id=framework_id,
            framework_name=framework.name,
            framework_version=framework.version,
            applicable_requirements=app_reqs,
            compliant=metrics["compliant"],
            partially_compliant=metrics["partial"],
            non_compliant=metrics["non_compliant"],
            insufficient_evidence=metrics["insufficient_evidence"],
            not_assessed=metrics["not_assessed"],
            not_applicable=metrics["not_applicable"],
            exceptions=metrics["exceptions"],
            coverage_percentage=round((metrics["compliant"] / app_reqs * 100) if app_reqs > 0 else 0, 2),
            evidence_coverage=round((metrics["total_evidence_completeness"] / app_reqs) if app_reqs > 0 else 0, 2),
            overall_confidence=round((metrics["total_confidence"] / app_reqs) if app_reqs > 0 else 0, 2),
            last_assessed=now
        )
        return summary

    def _create_gap(self, framework_id, requirement_id, control_id, gap_type, severity, description):
        return ComplianceGap(
            organization_id=self.org_id,
            framework_id=framework_id,
            requirement_id=requirement_id,
            control_id=control_id,
            gap_type=gap_type,
            severity=severity,
            description=description
        )

    def _load_applicability(self, framework_id) -> Dict[uuid.UUID, str]:
        # Would filter by framework ideally, but applicability is tied to requirement
        apps = self.db.query(ComplianceApplicability).filter(
            ComplianceApplicability.organization_id == self.org_id
        ).all()
        return {a.requirement_id: a.status for a in apps}

    def _load_mappings(self, framework_id) -> Dict[uuid.UUID, List[ComplianceControlMapping]]:
        mappings = self.db.query(ComplianceControlMapping).filter(
            ComplianceControlMapping.framework_id == framework_id
        ).all()
        res = {}
        for m in mappings:
            res.setdefault(m.requirement_id, []).append(m)
        return res

    def _load_controls(self) -> Dict[uuid.UUID, SecurityControl]:
        controls = self.db.query(SecurityControl).filter(
            SecurityControl.organization_id == self.org_id
        ).all()
        return {c.id: c for c in controls}

    def _load_evidence(self) -> Dict[uuid.UUID, List[ComplianceEvidence]]:
        evidence = self.db.query(ComplianceEvidence).filter(
            ComplianceEvidence.organization_id == self.org_id
        ).all()
        res = {}
        for e in evidence:
            res.setdefault(e.control_id, []).append(e)
        return res

    def _load_exceptions(self, framework_id) -> Dict[uuid.UUID, ComplianceException]:
        exceptions = self.db.query(ComplianceException).filter(
            ComplianceException.organization_id == self.org_id
        ).all()
        return {e.requirement_id: e for e in exceptions}

    def get_crosswalk(self, control_id: uuid.UUID) -> dict:
        """
        Return all framework requirements mapped to a specific control.
        """
        mappings = self.db.query(ComplianceControlMapping).filter(
            ComplianceControlMapping.control_id == control_id
        ).all()
        
        crosswalk = {}
        for m in mappings:
            req = self.db.query(ComplianceRequirement).filter(ComplianceRequirement.id == m.requirement_id).first()
            if req:
                fw = self.db.query(ComplianceFramework).filter(ComplianceFramework.id == req.framework_id).first()
                if fw:
                    crosswalk.setdefault(fw.name, []).append({
                        "requirement_id": req.requirement_id,
                        "title": req.title,
                        "mapping_type": m.mapping_type,
                        "coverage": m.coverage_percentage
                    })
        return crosswalk
