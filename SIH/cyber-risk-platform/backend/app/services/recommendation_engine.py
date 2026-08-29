import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.models.organization import Organization
from app.models.asset import Asset
from app.models.risk import RiskScore
from app.models.financial_risk import FinancialRiskAssessment
from app.models.vulnerability import Vulnerability
from app.models.threat_intel import ThreatIntelligenceRecord, ThreatIndicator, ThreatCorrelation
from app.models.recommendation import Recommendation
from app.models.prediction import RiskPrediction
from app.schemas.recommendation import RecommendationMetadata, RecommendationEvidence

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_recommendations(self, organization_id: uuid.UUID) -> List[Recommendation]:
        """
        Scan all assets in the organization and generate/update prioritized mitigations.
        """
        assets = self.db.scalars(select(Asset).where(Asset.organization_id == organization_id)).all()
        
        new_recommendations = []
        
        for asset in assets:
            # 1. Gather Evidence
            current_risk = self._get_current_risk(asset.id)
            if not current_risk:
                continue
                
            predicted_risk = self._get_predicted_risk(asset.id)
            fin_risk = self._get_financial_risk(asset.id)
            vulns = self._get_vulnerabilities(asset.id)
            threats = self._get_threats_for_asset(asset.id)
            
            # 2. Run deterministic rule matrix
            candidates = self._generate_candidates(asset, current_risk, predicted_risk, fin_risk, vulns, threats)
            
            # 3. Save to DB (In a real system, we'd deduplicate against existing open recommendations)
            for c in candidates:
                rec = Recommendation(
                    organization_id=organization_id,
                    asset_id=asset.id,
                    title=c["title"],
                    description=c["description"],
                    priority=c["priority"],
                    estimated_cost=c.get("estimated_cost"),
                    expected_risk_reduction=c.get("expected_risk_reduction"),
                    status="proposed",
                    generated_at=datetime.now(timezone.utc),
                    rec_metadata=c["metadata"].model_dump()
                )
                self.db.add(rec)
                new_recommendations.append(rec)
                
        self.db.commit()
        
        # Reload and sort by financial benefit / priority
        return self._get_active_recommendations(organization_id)
        
    def _get_current_risk(self, asset_id: uuid.UUID) -> Optional[RiskScore]:
        return self.db.scalars(select(RiskScore).where(RiskScore.asset_id == asset_id).order_by(desc(RiskScore.calculated_at)).limit(1)).first()

    def _get_predicted_risk(self, asset_id: uuid.UUID) -> Optional[RiskPrediction]:
        return self.db.scalars(select(RiskPrediction).where(RiskPrediction.asset_id == asset_id, RiskPrediction.forecast_horizon_days == 30).order_by(desc(RiskPrediction.prediction_timestamp)).limit(1)).first()

    def _get_financial_risk(self, asset_id: uuid.UUID) -> Optional[FinancialRiskAssessment]:
        return self.db.scalars(select(FinancialRiskAssessment).where(FinancialRiskAssessment.asset_id == asset_id).order_by(desc(FinancialRiskAssessment.calculated_at)).limit(1)).first()

    def _get_vulnerabilities(self, asset_id: uuid.UUID) -> List[Vulnerability]:
        return self.db.scalars(select(Vulnerability).where(Vulnerability.asset_id == asset_id, Vulnerability.status == "open")).all()
        
    def _get_threats_for_asset(self, asset_id: uuid.UUID) -> List[Any]:
        # Simple threat lookup via asset tags or OS for the demo
        asset = self.db.scalar(select(Asset).where(Asset.id == asset_id))
        if not asset:
            return []
            
        threats = []
        from app.models.threat_intel import ThreatCorrelation, ThreatIntelligenceRecord
        
        # Look for threats correlated with this asset
        records = self.db.scalars(
            select(ThreatIntelligenceRecord)
            .join(ThreatCorrelation, ThreatCorrelation.threat_record_id == ThreatIntelligenceRecord.id)
            .where(ThreatCorrelation.asset_id == asset_id)
        ).all()
        threats.extend(records)
            
        # Fallback to general active threats if no specific TI records
        if not threats:
            from app.models.threat import Threat
            general_threats = self.db.scalars(select(Threat).where(Threat.active == True)).all()
            threats.extend(general_threats)
            
        return threats

    def _generate_candidates(
        self, asset: Asset, current_risk: RiskScore, predicted_risk: Optional[RiskPrediction], 
        fin_risk: Optional[FinancialRiskAssessment], vulns: List[Vulnerability], threats: List[Any]
    ) -> List[Dict[str, Any]]:
        
        candidates = []
        eal = float(fin_risk.expected_loss) if fin_risk and fin_risk.expected_loss else 0.0
        
        # Rule 1: High Severity Vulnerability + Internet Exposed
        crit_vulns = [v for v in vulns if v.severity and v.severity.lower() in ["critical", "high"]]
        if asset.internet_exposed and crit_vulns:
            for v in crit_vulns:
                # Calculate risk reduction (e.g. 15 points)
                risk_reduction = 15.0 if v.severity.lower() == "critical" else 10.0
                fin_benefit = (risk_reduction / 100.0) * eal
                
                evidence = [RecommendationEvidence(
                    source="Vulnerability Scanner",
                    detail=f"Found {v.severity} vulnerability ({v.cve_id}) on internet-facing asset.",
                    severity=v.severity
                )]
                
                candidates.append({
                    "title": f"Patch {v.cve_id} on {asset.name}",
                    "description": f"An externally facing asset is exposing a {v.severity} vulnerability. Immediate patching is required to prevent exploitation.",
                    "priority": "Critical",
                    "expected_risk_reduction": risk_reduction,
                    "estimated_cost": 500.0, # Dummy cost
                    "metadata": RecommendationMetadata(
                        rationale="Internet-exposed vulnerabilities carry the highest probability of automated exploitation.",
                        risk_driver="Unpatched Vulnerability",
                        urgency="Immediate",
                        expected_financial_benefit=fin_benefit,
                        implementation_effort="Low",
                        confidence=95.0,
                        evidence=evidence
                    )
                })

        # Rule 2: Active Threat Intelligence Match
        if threats:
            for t in threats:
                if t.severity and t.severity.lower() in ["critical", "high"]:
                    risk_reduction = 20.0
                    fin_benefit = (risk_reduction / 100.0) * eal
                    
                    campaign_name = getattr(t, "campaign_name", getattr(t, "name", "Unknown Campaign"))
                    
                    evidence = [RecommendationEvidence(
                        source="Threat Intelligence",
                        detail=f"Active threat campaign '{campaign_name}' potentially targeting {asset.operating_system or 'this environment'}.",
                        severity=t.severity
                    )]
                    
                    candidates.append({
                        "title": f"Deploy IoC Blocks for {campaign_name}",
                        "description": f"Threat intelligence indicates an active campaign targeting your infrastructure. Deploy associated Indicators of Compromise (IoCs) to boundary firewalls and EDR.",
                        "priority": "High",
                        "expected_risk_reduction": risk_reduction,
                        "estimated_cost": 100.0,
                        "metadata": RecommendationMetadata(
                            rationale="Proactive blocking of known malicious infrastructure prevents initial access.",
                            risk_driver="Active Threat Campaign",
                            urgency="24 Hours",
                            expected_financial_benefit=fin_benefit,
                            implementation_effort="Medium",
                            confidence=85.0,
                            evidence=evidence
                        )
                    })

        # Rule 3: Rising Risk Trend Prediction
        if predicted_risk and predicted_risk.trend == "increasing" and (predicted_risk.predicted_risk - current_risk.score > 10):
            risk_reduction = predicted_risk.predicted_risk - current_risk.score
            fin_benefit = (risk_reduction / 100.0) * eal
            
            evidence = [RecommendationEvidence(
                source="AI Prediction Engine",
                detail=f"Risk forecasted to increase by {risk_reduction:.1f} points in the next 30 days.",
                severity="High"
            )]
            
            candidates.append({
                "title": f"Conduct Security Review of {asset.name}",
                "description": f"The AI engine predicts a significant increase in risk for this asset. A manual security review is recommended to identify emerging misconfigurations.",
                "priority": "Medium",
                "expected_risk_reduction": risk_reduction,
                "estimated_cost": 1500.0,
                "metadata": RecommendationMetadata(
                    rationale="Intervening before forecasted risk materializes reduces overall expected loss.",
                    risk_driver="Negative Risk Trend",
                    urgency="7 Days",
                    expected_financial_benefit=fin_benefit,
                    implementation_effort="High",
                    confidence=predicted_risk.confidence,
                    evidence=evidence
                )
            })

        return candidates

    def _get_active_recommendations(self, organization_id: uuid.UUID) -> List[Recommendation]:
        """
        Fetches proposed recommendations and sorts them by Financial Benefit (descending).
        """
        # In SQL Alchemy, ordering by a JSONB field value requires specific casting,
        # For simplicity, we can fetch all open ones and sort in Python.
        recs = self.db.scalars(
            select(Recommendation)
            .where(Recommendation.organization_id == organization_id)
            .where(Recommendation.status == "proposed")
        ).all()
        
        # Sort by priority, then by financial benefit
        priority_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        
        def get_sort_key(r: Recommendation):
            p_score = priority_map.get(r.priority, 0)
            fin = r.rec_metadata.get("expected_financial_benefit", 0.0) if r.rec_metadata else 0.0
            return (p_score, fin)
            
        return sorted(recs, key=get_sort_key, reverse=True)
