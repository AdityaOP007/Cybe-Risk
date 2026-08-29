import uuid
import math
from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.models.telemetry import TelemetryEvent
from app.models.threat_intel import ThreatCorrelation
from app.models.control import SecurityControl
from app.models.risk import RiskScore

class RiskEngine:
    """
    Core engine for calculating transparent and explainable cyber risk.
    """
    def __init__(self, db: Session):
        self.db = db

    def calculate_asset_risk(self, asset_id: uuid.UUID) -> RiskScore:
        """
        Calculates the risk for a single asset based on:
        - Criticality & Business Value
        - Exposure
        - Vulnerabilities
        - Telemetry
        - Threat Intelligence
        - Security Controls
        """
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")

        drivers: List[str] = []
        confidence_points = 0
        max_confidence = 100

        # 1. IMPACT CALCULATION
        # Criticality (0-100) -> 60% of impact
        criticality_impact = asset.criticality * 0.6
        if asset.criticality >= 80:
            drivers.append(f"Highly critical asset ({asset.criticality}/100)")
            confidence_points += 10
        elif asset.criticality > 0:
            confidence_points += 10

        # Business Value -> 30% of impact (Log normalized: $10k -> 0, $1M -> 15, $10M -> 30)
        # Using a simple scaling: $100M = 30 points.
        bv_points = min(30, (math.log10(max(1, asset.business_value)) / 8.0) * 30) if asset.business_value > 0 else 0
        if bv_points >= 20:
            drivers.append(f"High business value (${asset.business_value:,.0f})")
            confidence_points += 10
        elif asset.business_value > 0:
            confidence_points += 10

        # Exposure -> 10% of impact
        exposure_points = 10 if asset.internet_exposed else 0
        if asset.internet_exposed:
            drivers.append("Asset is internet exposed")
        confidence_points += 10 # We always know if it's exposed or not

        impact = min(100, criticality_impact + bv_points + exposure_points)


        # 2. LIKELIHOOD CALCULATION
        likelihood = 0.0
        
        # 2a. Vulnerabilities
        vulns = self.db.query(Vulnerability).filter(Vulnerability.asset_id == asset_id).all()
        if vulns:
            confidence_points += 20
            # Get max CVSS score (0-10) -> scales to 0-40 likelihood points
            max_cvss = max((v.cvss_score or 0) for v in vulns)
            likelihood += min(40, max_cvss * 4)
            if max_cvss >= 7.0:
                drivers.append(f"Contains high/critical vulnerabilities (Max CVSS: {max_cvss})")
        else:
            confidence_points += 10

        # 2b. Telemetry
        events = self.db.query(TelemetryEvent).filter(TelemetryEvent.asset_id == asset_id).all()
        if events:
            confidence_points += 25
            critical_events = sum(1 for e in events if e.severity == "critical")
            high_events = sum(1 for e in events if e.severity == "high")
            
            telemetry_score = min(30, (critical_events * 10) + (high_events * 5))
            likelihood += telemetry_score
            
            if critical_events > 0:
                drivers.append(f"Active critical security alerts detected ({critical_events})")
            elif high_events > 0:
                drivers.append(f"Active high security alerts detected ({high_events})")
        else:
            confidence_points += 10 # Lack of telemetry is still data, but less confident

        # 2c. Threat Intelligence
        correlations = self.db.query(ThreatCorrelation).filter(ThreatCorrelation.asset_id == asset_id).all()
        if correlations:
            confidence_points += 25
            # Are there any known exploited vulnerabilities correlated?
            known_exploited = False
            for corr in correlations:
                # Need to load the threat record
                threat = corr.threat_record
                if threat and threat.known_exploited:
                    known_exploited = True
                    break
            
            if known_exploited:
                likelihood += 30 # Massive bump
                drivers.append("Vulnerable to a Known Exploited threat (CISA KEV)")
            else:
                likelihood += 10 # Base threat intel bump
                drivers.append("Correlated with active external threat intelligence")
        else:
            confidence_points += 10

        likelihood = min(100, likelihood)
        
        # Set base likelihood if 0 to prevent 0 risk on critical assets
        if likelihood == 0:
            likelihood = 10 # Ambient risk

        # 3. GROSS RISK
        gross_risk = (impact * likelihood) / 100.0


        # 4. MITIGATION (SECURITY CONTROLS)
        controls = self.db.query(SecurityControl).filter(
            SecurityControl.organization_id == asset.organization_id,
            SecurityControl.status == "active"
        ).all()
        
        mitigation_factor = 0.0
        if controls:
            total_effectiveness = 0.0
            for ctrl in controls:
                cov = (ctrl.coverage_percentage or 0) / 100.0
                eff = (ctrl.effectiveness_percentage or 0) / 100.0
                total_effectiveness += (cov * eff)
            
            # Average effectiveness across all active controls
            avg_effectiveness = total_effectiveness / len(controls)
            # Max mitigation is 80% (cannot reduce risk to 0)
            mitigation_factor = min(0.8, avg_effectiveness)
            
            if mitigation_factor > 0.4:
                drivers.append(f"Strong organizational security controls mitigate {mitigation_factor*100:.0f}% of risk")
            elif mitigation_factor > 0:
                drivers.append(f"Partial security controls mitigate {mitigation_factor*100:.0f}% of risk")
        else:
            drivers.append("No active security controls mapped to mitigate risk")

        # 5. NET RISK
        net_risk = gross_risk * (1.0 - mitigation_factor)
        
        # 6. RISK LEVEL CLASSIFICATION
        if net_risk >= 80:
            level = "critical"
        elif net_risk >= 60:
            level = "high"
        elif net_risk >= 40:
            level = "medium"
        elif net_risk >= 20:
            level = "low"
        else:
            level = "informational"

        if len(drivers) == 0:
            drivers.append("Asset has low intrinsic value and no active threats")

        explanation = f"Asset '{asset.name}' has a {level.upper()} net risk score of {net_risk:.1f}. "
        explanation += f"This is driven by an impact score of {impact:.1f} and likelihood of {likelihood:.1f}, "
        explanation += f"offset by a {mitigation_factor*100:.1f}% control mitigation factor."

        metadata = {
            "factors": {
                "impact": round(impact, 2),
                "likelihood": round(likelihood, 2),
                "gross_risk": round(gross_risk, 2),
                "mitigation_factor": round(mitigation_factor, 4)
            },
            "drivers": drivers,
            "explanation": explanation,
            "confidence": min(100, confidence_points)
        }

        # Create RiskScore record
        risk_record = RiskScore(
            organization_id=asset.organization_id,
            asset_id=asset.id,
            score=round(net_risk, 2),
            risk_level=level,
            calculation_version="v1.0",
            risk_metadata=metadata
        )
        
        self.db.add(risk_record)
        self.db.commit()
        self.db.refresh(risk_record)
        
        return risk_record

    def calculate_organization_risk(self, organization_id: uuid.UUID) -> RiskScore:
        """
        Aggregates risk across all assets for the organization.
        """
        # First, recalculate risk for all assets to ensure it's up to date
        assets = self.db.query(Asset).filter(Asset.organization_id == organization_id).all()
        
        if not assets:
            # Handle empty org
            risk_record = RiskScore(
                organization_id=organization_id,
                score=0,
                risk_level="informational",
                calculation_version="v1.0",
                risk_metadata={
                    "drivers": ["No assets found in organization"],
                    "explanation": "Organizational risk is 0 because there are no assets.",
                    "confidence": 100.0
                }
            )
            self.db.add(risk_record)
            self.db.commit()
            return risk_record
            
        asset_scores = []
        for asset in assets:
            score_record = self.calculate_asset_risk(asset.id)
            asset_scores.append(score_record)
            
        # Aggregate logic: We don't just take the average. 
        # A single critical asset compromised can compromise the organization.
        # We will use a weighted average favoring high-risk critical assets.
        
        total_weight = 0
        weighted_sum = 0
        
        critical_assets_count = 0
        
        for score in asset_scores:
            # Weight is based on the asset's criticality
            # If criticality is 0, we still give it a weight of 1 so it counts
            asset = score.asset
            weight = max(1, asset.criticality)
            
            weighted_sum += (score.score * weight)
            total_weight += weight
            
            if score.risk_level in ["critical", "high"]:
                critical_assets_count += 1
                
        org_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        if org_score >= 80:
            level = "critical"
        elif org_score >= 60:
            level = "high"
        elif org_score >= 40:
            level = "medium"
        elif org_score >= 20:
            level = "low"
        else:
            level = "informational"
            
        drivers = [
            f"Organization has {len(assets)} total assets.",
            f"{critical_assets_count} assets are currently at High or Critical risk."
        ]
        
        explanation = f"Organizational net risk is {org_score:.1f} ({level.upper()}), aggregated across {len(assets)} assets."

        metadata = {
            "factors": {
                "total_assets": len(assets),
                "critical_assets": critical_assets_count
            },
            "drivers": drivers,
            "explanation": explanation,
            "confidence": 90 # Aggregated confidence
        }
        
        risk_record = RiskScore(
            organization_id=organization_id,
            score=round(org_score, 2),
            risk_level=level,
            calculation_version="v1.0",
            risk_metadata=metadata
        )
        
        self.db.add(risk_record)
        self.db.commit()
        self.db.refresh(risk_record)
        
        return risk_record
