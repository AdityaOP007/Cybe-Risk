import logging
from app.core.database import SessionLocal
from app.models.organization import Organization
from app.services.recommendation_engine import RecommendationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate():
    db = SessionLocal()
    
    org = db.query(Organization).first()
    if not org:
        logger.error("No organization found. Run seed_database.py first.")
        return

    logger.info(f"Generating recommendations for organization: {org.name}...")
    
    engine = RecommendationEngine(db)
    recs = engine.generate_recommendations(org.id)
    
    logger.info("="*50)
    logger.info(f"GENERATED {len(recs)} RECOMMENDATIONS")
    logger.info("="*50)
    for r in recs:
        logger.info(f"[{r.priority}] {r.title}")
        if r.metadata_:
            logger.info(f"  Urgency : {r.metadata_.get('urgency')}")
            logger.info(f"  Benefit : ₹{(r.metadata_.get('expected_financial_benefit', 0) / 10000000):.2f} Cr")
        logger.info("-" * 30)

if __name__ == "__main__":
    generate()
