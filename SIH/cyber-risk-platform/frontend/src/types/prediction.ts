export interface PredictionDriver {
  feature: string;
  importance: number;
  direction: 'increasing' | 'decreasing' | 'stable';
  description: string;
}

export interface RiskPrediction {
  id: string;
  organization_id: string;
  asset_id: string;
  risk_score_id: string;
  
  forecast_horizon_days: number;
  predicted_risk: number;
  lower_bound: number;
  upper_bound: number;
  
  trend: 'increasing' | 'decreasing' | 'stable';
  confidence: number;
  
  predicted_financial_exposure?: number;
  financial_lower_bound?: number;
  financial_upper_bound?: number;
  
  model_name: string;
  model_version: string;
  
  prediction_timestamp: string;
  created_at: string;
}

export interface AssetRiskForecastResponse {
  asset_id: string;
  current_risk: number;
  current_financial_exposure?: number;
  forecasts: Record<number, RiskPrediction>;
  drivers: PredictionDriver[];
}

export interface PredictionModel {
  id: string;
  name: string;
  version: string;
  model_type: string;
  dataset_version: string;
  feature_version: string;
  status: string;
  metrics: Record<string, any> | null;
  training_completed_at: string;
}

export interface PredictionBulkResult {
  assets_processed: number;
  predictions_generated: number;
  insufficient_data: number;
  failed: number;
}
