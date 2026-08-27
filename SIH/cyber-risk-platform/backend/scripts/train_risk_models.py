import logging
from app.core.database import SessionLocal
from app.services.prediction.training import PredictionTrainingPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train():
    db = SessionLocal()
    pipeline = PredictionTrainingPipeline(db)
    
    logger.info("Building dataset from historical RiskScores...")
    df = pipeline.build_dataset()
    logger.info(f"Dataset built. Total records: {len(df)}")
    
    if len(df) < 30:
        logger.error("Insufficient data. Please run 'python scripts/generate_risk_history.py' first.")
        return

    logger.info("Executing training pipeline (Walk-forward validation)...")
    model_record = pipeline.run_pipeline()
    
    logger.info("="*50)
    logger.info("TRAINING COMPLETE")
    logger.info("="*50)
    logger.info(f"Model Name     : {model_record.name}")
    logger.info(f"Model Version  : {model_record.version}")
    logger.info(f"Model Type     : {model_record.model_type}")
    logger.info(f"Validation MAE : {model_record.metrics.get('mae'):.4f}")
    logger.info(f"Baseline MAE   : {model_record.metrics.get('baseline_mae'):.4f}")
    logger.info(f"Artifact Path  : {model_record.artifact_path}")
    logger.info("="*50)

if __name__ == "__main__":
    train()
