import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.asset import Asset
from app.models.risk import RiskScore
from app.models.financial_risk import FinancialAssumption, FinancialRiskAssessment

class FinancialRiskEngine:
    """
    Engine for translating cyber risk into financial consequences.
    """
    def __init__(self, db: Session):
        self.db = db

    def _get_assumptions(self, organization_id: uuid.UUID) -> Dict[str, FinancialAssumption]:
        assumptions = self.db.query(FinancialAssumption).filter(
            FinancialAssumption.organization_id == organization_id,
            (FinancialAssumption.effective_until == None) | (FinancialAssumption.effective_until > func.now())
        ).all()
        return {a.category: a for a in assumptions}

    def _get_assumption_value(self, assumptions_dict: Dict[str, FinancialAssumption], category: str, default: float) -> float:
        if category in assumptions_dict:
            return float(assumptions_dict[category].value)
        return default

    def calculate_asset_financial_risk(self, asset_id: uuid.UUID) -> FinancialRiskAssessment:
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")

        # 1. Load latest Cyber Risk
        latest_risk = self.db.query(RiskScore).filter(RiskScore.asset_id == asset_id).order_by(desc(RiskScore.calculated_at)).first()
        if not latest_risk:
            raise ValueError(f"No cyber risk score found for asset {asset_id}. Run RiskEngine first.")

        # 2. Load Assumptions
        assumptions = self._get_assumptions(asset.organization_id)
        assumptions_snapshot = {k: {"value": float(v.value), "unit": v.unit, "confidence": v.confidence} for k, v in assumptions.items()}

        # Explanation generation lists
        drivers = []
        
        # We start with 100% confidence, reduced by missing critical assumptions
        confidence = 100.0
        missing_data_penalties = 0

        # --- FINANCIAL MODEL IMPACT CALCULATIONS ---

        # A. Business Interruption
        downtime_hours = self._get_assumption_value(assumptions, "downtime_hours", 0)
        revenue_impact_per_hour = self._get_assumption_value(assumptions, "revenue_impact_per_hour", 0)
        if downtime_hours > 0 and revenue_impact_per_hour > 0:
            business_interruption_loss = downtime_hours * revenue_impact_per_hour
            drivers.append(f"Business Interruption: {downtime_hours} hours downtime at ₹{revenue_impact_per_hour:,.0f}/hr")
        else:
            business_interruption_loss = 0
            missing_data_penalties += 10

        # B. Data Loss
        affected_records = self._get_assumption_value(assumptions, "affected_records", 0)
        cost_per_record = self._get_assumption_value(assumptions, "cost_per_record", 0)
        if affected_records > 0 and cost_per_record > 0:
            data_loss = affected_records * cost_per_record
            drivers.append(f"Data Loss: {affected_records:,} records at ₹{cost_per_record:,.0f}/record")
        else:
            data_loss = 0

        # C. Recovery Cost
        recovery_loss = self._get_assumption_value(assumptions, "recovery_cost", 0)
        if recovery_loss > 0:
            drivers.append(f"Recovery Costs: Estimated at ₹{recovery_loss:,.0f}")
        else:
            missing_data_penalties += 10

        # D. Direct Loss (e.g. Incident Response, Forensics baseline)
        direct_loss = self._get_assumption_value(assumptions, "incident_response_cost", 0)
        if direct_loss > 0:
            drivers.append(f"Direct/IR Costs: Estimated at ₹{direct_loss:,.0f}")

        # E. Customer Impact
        customer_impact = self._get_assumption_value(assumptions, "customer_impact", 0)
        if customer_impact > 0:
            drivers.append(f"Customer Impact/Notification: ₹{customer_impact:,.0f}")

        # F. Third-Party Impact
        third_party_impact = self._get_assumption_value(assumptions, "third_party_impact", 0)

        # G. Regulatory / Legal
        regulatory_legal_exposure = self._get_assumption_value(assumptions, "regulatory_legal_estimate", 0)
        if regulatory_legal_exposure > 0:
            drivers.append(f"Regulatory/Legal Exposure: Modeled at ₹{regulatory_legal_exposure:,.0f}")

        # H. Fraud Loss
        fraud_loss = self._get_assumption_value(assumptions, "fraud_loss_estimate", 0)
        
        # I. Reputation / Revenue Impact (Long-term)
        reputation_revenue_impact = self._get_assumption_value(assumptions, "reputation_revenue_impact", 0)

        # 3. Aggregate Potential Loss
        potential_loss = (
            direct_loss + data_loss + business_interruption_loss + recovery_loss +
            customer_impact + third_party_impact + regulatory_legal_exposure +
            fraud_loss + reputation_revenue_impact
        )

        # 4. Determine Event Frequency
        # If explicit frequency is not in assumptions, we derive it from the cyber risk likelihood
        # We extract likelihood from the metadata if it exists, otherwise use the final risk score / 100 as a very rough proxy.
        explicit_frequency = self._get_assumption_value(assumptions, "annual_event_frequency", -1)
        if explicit_frequency >= 0:
            annual_event_frequency = explicit_frequency
            drivers.append(f"Event Frequency: Explicitly assumed at {annual_event_frequency} events/year")
        else:
            # Derive from module 6 likelihood
            likelihood_factor = 0.5 # default moderate
            if latest_risk.metadata_ and "factors" in latest_risk.metadata_:
                # Likelihood is 0-100 in Module 6
                likelihood_factor = latest_risk.metadata_["factors"].get("likelihood", 50) / 100.0
            
            # Map likelihood (0.0 - 1.0) to an annualized frequency (e.g., 0.1 = 1 in 10 years, 0.9 = nearly 1 a year)
            annual_event_frequency = likelihood_factor
            drivers.append(f"Event Frequency: Derived from Cyber Risk likelihood ({annual_event_frequency:.2f} events/year)")

        # 5. Expected Loss
        expected_loss = potential_loss * annual_event_frequency
        annualized_expected_loss = expected_loss # They are synonymous in this annual model

        # Adjust Confidence
        final_confidence = max(0, confidence - missing_data_penalties)
        if "confidence" in latest_risk.metadata_:
            # Blend with cyber risk confidence
            cyber_conf = latest_risk.metadata_.get("confidence", 100)
            final_confidence = (final_confidence + cyber_conf) / 2.0

        explanation = f"Asset '{asset.name}' has a modeled Potential Loss of ₹{potential_loss:,.0f}. "
        explanation += f"With an annualized event frequency of {annual_event_frequency:.2f}, the Expected Annual Loss is ₹{expected_loss:,.0f}."

        metadata = {
            "drivers": drivers,
            "explanation": explanation,
            "annual_event_frequency": round(annual_event_frequency, 4)
        }

        record = FinancialRiskAssessment(
            organization_id=asset.organization_id,
            asset_id=asset.id,
            risk_score_id=latest_risk.id,
            potential_loss=potential_loss,
            expected_loss=expected_loss,
            annualized_expected_loss=annualized_expected_loss,
            direct_loss=direct_loss,
            data_loss=data_loss,
            business_interruption_loss=business_interruption_loss,
            recovery_loss=recovery_loss,
            customer_impact=customer_impact,
            third_party_impact=third_party_impact,
            regulatory_legal_exposure=regulatory_legal_exposure,
            fraud_loss=fraud_loss,
            reputation_revenue_impact=reputation_revenue_impact,
            confidence=round(final_confidence, 2),
            data_completeness=100.0 - missing_data_penalties, # Rough completeness metric
            calculation_version="v1.0",
            assumptions_snapshot=assumptions_snapshot,
            metadata_=metadata
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        return record

    def calculate_organization_financial_risk(self, organization_id: uuid.UUID) -> None:
        """
        Recalculates financial risk for all assets in the organization.
        Aggregation logic is handled via querying, this just ensures freshness.
        """
        assets = self.db.query(Asset).filter(Asset.organization_id == organization_id).all()
        for asset in assets:
            # Only calculate if they have a cyber risk score
            has_risk = self.db.query(RiskScore).filter(RiskScore.asset_id == asset.id).first()
            if has_risk:
                self.calculate_asset_financial_risk(asset.id)
