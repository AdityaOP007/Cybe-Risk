export interface RiskFactors {
  impact: number;
  likelihood: number;
  gross_risk: number;
  mitigation_factor: number;
  total_assets?: number;
  critical_assets?: number;
}

export interface RiskMetadata {
  factors: RiskFactors;
  drivers: string[];
  explanation: string;
  confidence: number;
}

export interface RiskScore {
  id: string;
  organization_id: string;
  asset_id?: string;
  score: number;
  risk_level: string;
  calculation_version: string;
  metadata_: RiskMetadata;
  calculated_at: string;
  created_at: string;
}

export interface RiskTrendDataPoint {
  timestamp: string;
  score: number;
  risk_level: string;
}

export interface RiskTrendResponse {
  current_score: RiskScore;
  historical_trend: RiskTrendDataPoint[];
}
