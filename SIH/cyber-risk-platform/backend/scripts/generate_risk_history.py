import logging
import random
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.asset import Asset
from app.models.risk import RiskScore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_history():
    db = SessionLocal()
    
    # Get the default test organization
    org = db.query(Organization).first()
    if not org:
        logger.error("No organization found. Run seed_database.py first.")
        return

    assets = db.query(Asset).filter(Asset.organization_id == org.id).all()
    if not assets:
        logger.error("No assets found.")
        return
        
    logger.info(f"Generating 90 days of synthetic historical risk for {len(assets)} assets...")
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=90)
    
    db.query(RiskScore).filter(RiskScore.asset_id.in_([a.id for a in assets])).delete()
    db.commit()

    records_created = 0

    for asset in assets:
        # Generate a synthetic path for this asset
        current_date = start_date
        
        # Base risk profile based on asset environment
        base_score = 40.0
        if asset.environment == "Production":
            base_score = 65.0
        elif asset.internet_exposed:
            base_score = 75.0
            
        current_score = base_score
            
        while current_date <= end_date:
            # Add some random walk / volatility
            volatility = random.uniform(-2.5, 2.5)
            
            # Simulate a "Critical Vulnerability Discovered" event (rare spike)
            if random.random() < 0.02:
                volatility += random.uniform(15.0, 25.0)
            
            # Simulate a "Control Improved / Patch applied" event (drop)
            elif random.random() < 0.05:
                volatility -= random.uniform(5.0, 15.0)
                
            current_score += volatility
            current_score = max(0.0, min(100.0, current_score)) # Clamp 0-100
            
            likelihood = current_score / 100.0
            impact = min(10.0, base_score / 10.0) # simplify
            
            # Confidence generally starts low and gets higher
            days_passed = (current_date - start_date).days
            confidence = min(95.0, 50.0 + (days_passed * 0.5) + random.uniform(-5, 5))
            
            score = RiskScore(
                organization_id=org.id,
                asset_id=asset.id,
                score=current_score,
                risk_level="High" if current_score > 70 else "Medium" if current_score > 40 else "Low",
                metadata_={
                    "synthetic_history": True,
                    "simulated_date": current_date.isoformat(),
                    "likelihood": likelihood,
                    "impact": impact,
                    "confidence": confidence
                },
                calculated_at=current_date,
                created_at=current_date
            )
            db.add(score)
            records_created += 1
            
            current_date += timedelta(days=1)

    db.commit()
    logger.info(f"Successfully generated {records_created} synthetic historical records.")

if __name__ == "__main__":
    generate_history()
