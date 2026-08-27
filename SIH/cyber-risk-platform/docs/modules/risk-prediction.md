# Module 08: AI-Powered Cyber Risk Prediction & Forecasting

## Overview
The AI-Powered Risk Prediction module uses historical cyber risk data, threat intelligence, and telemetry to forecast where organizational or asset-level risk is heading over the next 7, 30, and 90 days.

Unlike simplistic black-box AI tools, this system implements rigorous, backtested Machine Learning (using Scikit-Learn's `RandomForestRegressor`) and relies solely on deterministic data rather than fabricated likelihoods.

## Architecture & Data Flow

1. **Synthetic & Historical Data**
   - The platform continuously saves calculated point-in-time Risk Scores (Module 06).
   - A dataset builder constructs time-series datasets shifting forward by the prediction horizon to generate a target feature.

2. **Walk-Forward Validation**
   - Because cyber-risk data is sequential (time-series), we do not use simple K-Fold cross-validation.
   - The model is trained using `TimeSeriesSplit` (Walk-Forward Validation). It trains on past data to predict future data.

3. **Baseline Comparison**
   - Before accepting a Machine Learning model, the system compares its Mean Absolute Error (MAE) against a naïve `DummyRegressor` baseline (which simply predicts the historical average).
   - If the ML model fails to beat the baseline, the system defaults to the baseline to prevent deploying a complex model that offers no actual predictive value.

4. **Model Registry**
   - Trained models are registered in the `RiskPredictionModel` table.
   - We store the model binary as a `.joblib` artifact (in `models/`), tracking the version, dataset metrics, MAE/RMSE, and training period.

## Prediction Mechanics

- **Target**: The forecasted `RiskScore` (0–100 scale).
- **Intervals**: Prediction bounds are dynamically calculated using the MAE, widening as the forecast horizon increases (e.g., 90 days has a wider interval than 7 days).
- **Confidence**: Based heavily on data completeness (inherited from Module 06) and degraded mathematically for longer prediction horizons.
- **Financial Mapping**: The engine deterministically maps the forecasted cyber risk back into the Financial Risk engine (Module 07) to calculate the Forecasted Expected Annual Loss without reinventing financial formulas.

## Security & Data Leakage Prevention

- We strictly prevent **Future Data Leakage** by only extracting features (e.g. current risk score, likelihood, impact, confidence) that are available at time `T` to predict `T+h`.
- The frontend explicitly warns users that these are statistical forecasts and not absolute guarantees of attack probabilities.

## Commands

- **Generate Synthetic History**: `python scripts/generate_risk_history.py` (useful for demos without 90 days of organic platform usage).
- **Train Models**: `python scripts/train_risk_models.py` (executes the Walk-Forward Validation pipeline, registers the model).

## UI/Frontend

The user interface under **Risk Forecast** exposes:
1. The 7, 30, and 90-day intervals.
2. The current vs forecasted risk score.
3. Extracted feature drivers explaining the prediction.
4. The exact ML model algorithm, version, and training timestamp for transparency.
