import logging
import uuid
from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.recommendation import Recommendation
from app.models.optimization import CybersecurityInvestment
from app.schemas.optimization import OptimizationRunRequest, OptimizationWeights
from app.services.optimization.engine import OptimizationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_demo():
    db = SessionLocal()
    org = db.query(Organization).first()
    if not org:
        logger.error("No organization found. Run seed_database.py first.")
        return

    # Delete existing candidates
    db.query(CybersecurityInvestment).filter(CybersecurityInvestment.organization_id == org.id).delete()
    db.commit()

    # Get active recommendations from Module 9
    recs = db.query(Recommendation).filter(Recommendation.organization_id == org.id, Recommendation.status == "proposed").all()

    candidates = []
    # 1. Convert actual recommendations to investments
    for r in recs:
        fin_red = r.metadata_.get("expected_financial_benefit", 0.0) if r.metadata_ else 0.0
        urgency = r.metadata_.get("urgency", "Medium") if r.metadata_ else "Medium"
        effort = r.metadata_.get("implementation_effort", "Medium") if r.metadata_ else "Medium"
        
        inv = CybersecurityInvestment(
            organization_id=org.id,
            recommendation_id=r.id,
            asset_id=r.asset_id,
            title=r.title,
            description=r.description,
            cost=r.estimated_cost or 500000.0, # Default 5L
            risk_reduction=r.expected_risk_reduction,
            financial_reduction=fin_red,
            confidence=r.metadata_.get("confidence", 80.0) if r.metadata_ else 80.0,
            priority=r.priority,
            urgency=urgency,
            implementation_effort=effort,
            status="candidate"
        )
        candidates.append(inv)
        
    # 2. Add some purely synthetic ones to make optimization interesting
    synthetic = [
        CybersecurityInvestment(
            organization_id=org.id,
            title="Deploy Zero Trust Network Architecture",
            description="Organization-wide implementation of ZTNA, replacing traditional VPNs.",
            cost=2500000.0, # 25L
            risk_reduction=18.5,
            financial_reduction=35000000.0, # 3.5Cr
            confidence=85.0,
            priority="High",
            urgency="30 Days",
            status="candidate"
        ),
        CybersecurityInvestment(
            organization_id=org.id,
            title="Expand EDR Coverage to Legacy Systems",
            description="Deploy lightweight EDR agents to legacy manufacturing and ATM servers.",
            cost=1200000.0, # 12L
            risk_reduction=8.0,
            financial_reduction=12000000.0,
            confidence=90.0,
            priority="Medium",
            urgency="7 Days",
            status="candidate"
        ),
        CybersecurityInvestment(
            organization_id=org.id,
            title="Implement Data Loss Prevention (DLP)",
            description="Deploy DLP across endpoints and cloud storage to prevent data exfiltration.",
            cost=1800000.0, # 18L
            risk_reduction=12.0,
            financial_reduction=40000000.0,
            confidence=75.0,
            priority="High",
            urgency="30 Days",
            status="candidate"
        ),
        CybersecurityInvestment(
            organization_id=org.id,
            title="Automated Penetration Testing Subscription",
            description="Continuous automated pentesting for internet-facing assets.",
            cost=500000.0, # 5L
            cost_type="annual",
            annualized_cost=500000.0,
            risk_reduction=5.0,
            financial_reduction=5000000.0,
            confidence=95.0,
            priority="Medium",
            urgency="30 Days",
            status="candidate"
        )
    ]
    candidates.extend(synthetic)
    
    db.add_all(candidates)
    db.commit()
    logger.info(f"Seeded {len(candidates)} investment candidates.")
    
    # 3. Generate a default optimization run at 25 Lakh
    engine = OptimizationEngine(db, org.id)
    req = OptimizationRunRequest(
        budget=2500000.0,
        currency="INR",
        objective="balanced",
        weights=OptimizationWeights()
    )
    run = engine.run_optimization(req)
    logger.info(f"Generated default run. Selected {len(run.portfolios[0].selected_investments)} items. Cost: {run.total_cost}")

if __name__ == "__main__":
    seed_demo()
