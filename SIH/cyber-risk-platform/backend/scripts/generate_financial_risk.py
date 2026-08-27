import logging
from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.asset import Asset
from app.models.financial_risk import FinancialAssumption
from app.services.financial_risk.engine import FinancialRiskEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_financial_risk():
    db = SessionLocal()
    try:
        # Check for demo org
        org = db.query(Organization).first()
        if not org:
            logger.error("No organization found. Please run main seed_database.py first.")
            return

        # Create basic synthetic assumptions for the organization
        # We will delete existing ones first to ensure idempotency
        db.query(FinancialAssumption).filter(FinancialAssumption.organization_id == org.id).delete()
        db.commit()

        assumptions = [
            FinancialAssumption(
                organization_id=org.id, category="downtime_hours", name="Estimated Maximum Downtime", 
                value=24, unit="hours", source="synthetic_demo"
            ),
            FinancialAssumption(
                organization_id=org.id, category="revenue_impact_per_hour", name="Revenue Impact Per Hour", 
                value=500000, unit="INR", source="synthetic_demo"
            ),
            FinancialAssumption(
                organization_id=org.id, category="recovery_cost", name="Infrastructure Recovery Cost", 
                value=2500000, unit="INR", source="synthetic_demo"
            ),
            FinancialAssumption(
                organization_id=org.id, category="incident_response_cost", name="Incident Response Retainer/Fees", 
                value=1500000, unit="INR", source="synthetic_demo"
            ),
            FinancialAssumption(
                organization_id=org.id, category="affected_records", name="Potential Data Records Affected", 
                value=100000, unit="records", source="synthetic_demo"
            ),
            FinancialAssumption(
                organization_id=org.id, category="cost_per_record", name="Cost Per Record (Notification/Legal)", 
                value=250, unit="INR", source="synthetic_demo"
            ),
            FinancialAssumption(
                organization_id=org.id, category="customer_impact", name="Customer Compensation", 
                value=1000000, unit="INR", source="synthetic_demo"
            ),
            FinancialAssumption(
                organization_id=org.id, category="regulatory_legal_estimate", name="Regulatory/Legal Exposure", 
                value=5000000, unit="INR", source="synthetic_demo"
            )
        ]
        
        db.add_all(assumptions)
        db.commit()
        logger.info("Inserted synthetic financial assumptions.")

        # Trigger financial calculation for all assets
        engine = FinancialRiskEngine(db)
        engine.calculate_organization_financial_risk(org.id)
        logger.info(f"Calculated financial risk for all assets in org {org.id}")

    except Exception as e:
        logger.error(f"Failed to seed financial risk: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_financial_risk()
