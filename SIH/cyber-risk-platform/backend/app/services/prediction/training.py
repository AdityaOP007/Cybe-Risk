import uuid
import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, asc
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

from app.models.prediction import RiskPredictionModel
from app.models.risk import RiskScore

class PredictionTrainingPipeline:
    """
    Pipeline for training, evaluating, and registering cyber risk prediction models.
    """
    def __init__(self, db: Session, models_dir: str = "models/"):
        self.db = db
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)

    def build_dataset(self) -> pd.DataFrame:
        """
        Builds a time-series dataset from historical RiskScores.
        For simplicity, this uses the score as target, and shifts features for lag.
        """
        records = self.db.scalars(
            select(RiskScore).order_by(asc(RiskScore.calculated_at))
        ).all()

        if not records:
            return pd.DataFrame()

        data = []
        for r in records:
            data.append({
                "asset_id": str(r.asset_id),
                "calculated_at": r.calculated_at,
                "score": r.score,
                "likelihood": r.metadata_.get("likelihood", r.score / 100.0) if r.metadata_ else r.score / 100.0,
                "impact": r.metadata_.get("impact", 5.0) if r.metadata_ else 5.0,
                "confidence": r.metadata_.get("confidence", 80.0) if r.metadata_ else 80.0,
            })
            
        df = pd.DataFrame(data)
        df["calculated_at"] = pd.to_datetime(df["calculated_at"])
        df = df.sort_values(by=["asset_id", "calculated_at"])
        
        # We want to predict future risk. Let's create a target for T+7 days (for training simplicity, we just shift by 1 row if it's daily data).
        # In a real scenario, we'd resample to daily and shift by exactly 7 days.
        # For the demo, we'll just shift the target by 1 row (assuming daily).
        df["target_score"] = df.groupby("asset_id")["score"].shift(-1)
        
        # Drop rows where we don't have a future target to train on
        df = df.dropna(subset=["target_score"])
        
        return df

    def run_pipeline(self) -> RiskPredictionModel:
        """
        Executes the full pipeline: build data, train models, compare, and register best.
        """
        training_start = datetime.now(timezone.utc)
        
        df = self.build_dataset()
        if len(df) < 30:
            raise ValueError("Insufficient historical data for reliable prediction. Require at least 30 observations.")

        # Features
        features = ["score", "likelihood", "impact", "confidence"]
        X = df[features]
        y = df["target_score"]

        # Walk-forward validation (TimeSeriesSplit)
        tscv = TimeSeriesSplit(n_splits=3)
        
        # Candidate 1: Baseline (predicts recent average)
        dummy_model = DummyRegressor(strategy="mean")
        dummy_maes = []
        
        # Candidate 2: Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_maes = []

        for train_index, test_index in tscv.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            # Baseline
            dummy_model.fit(X_train, y_train)
            dummy_preds = dummy_model.predict(X_test)
            dummy_maes.append(mean_absolute_error(y_test, dummy_preds))
            
            # RF
            rf_model.fit(X_train, y_train)
            rf_preds = rf_model.predict(X_test)
            rf_maes.append(mean_absolute_error(y_test, rf_preds))

        baseline_mae = np.mean(dummy_maes)
        rf_mae = np.mean(rf_maes)

        # Select Best Model
        if rf_mae < baseline_mae:
            best_model = rf_model
            model_type = "RandomForestRegressor"
            final_mae = rf_mae
            # Train on full dataset
            best_model.fit(X, y)
            final_preds = best_model.predict(X)
        else:
            best_model = dummy_model
            model_type = "DummyRegressor"
            final_mae = baseline_mae
            # Train on full dataset
            best_model.fit(X, y)
            final_preds = best_model.predict(X)

        final_rmse = root_mean_squared_error(y, final_preds)
        final_r2 = r2_score(y, final_preds)
        
        # Save artifact
        version = f"v{training_start.strftime('%Y%m%d%H%M')}"
        model_name = "cyber_risk_forecaster"
        artifact_path = os.path.join(self.models_dir, f"{model_name}_{version}.joblib")
        joblib.dump(best_model, artifact_path)

        # Register in DB
        metrics = {
            "mae": float(final_mae),
            "rmse": float(final_rmse),
            "r2": float(final_r2),
            "baseline_mae": float(baseline_mae)
        }
        
        # Deactivate previous active models
        self.db.query(RiskPredictionModel).filter(RiskPredictionModel.status == "active").update({"status": "archived"})

        registry_record = RiskPredictionModel(
            name=model_name,
            version=version,
            model_type=model_type,
            dataset_version="ds_1.0",
            feature_version="fv_1.0",
            metrics=metrics,
            hyperparameters={"random_state": 42} if model_type == "RandomForestRegressor" else {},
            training_started_at=training_start,
            training_completed_at=datetime.now(timezone.utc),
            training_data_start=df["calculated_at"].min(),
            training_data_end=df["calculated_at"].max(),
            status="active",
            artifact_path=artifact_path
        )

        self.db.add(registry_record)
        self.db.commit()
        self.db.refresh(registry_record)

        return registry_record
