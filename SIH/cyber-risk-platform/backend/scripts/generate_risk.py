import json
import logging
from app.core.database import SessionLocal
from app.models.asset import Asset
from app.models.organization import Organization
from app.services.risk_engine import RiskEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_risk_scores():
    db = SessionLocal()
    try:
        engine = RiskEngine(db)
        
        # Calculate risk for all assets
        assets = db.query(Asset).all()
        logger.info(f"Calculating risk for {len(assets)} assets...")
        
        for asset in assets:
            engine.calculate_asset_risk(asset.id)
            
        # Calculate risk for all organizations
        orgs = db.query(Organization).all()
        logger.info(f"Calculating organizational risk for {len(orgs)} organizations...")
        
        for org in orgs:
            engine.calculate_organization_risk(org.id)
            
        logger.info("Risk calculation complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_risk_scores()
