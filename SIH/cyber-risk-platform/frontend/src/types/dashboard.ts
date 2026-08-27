export interface RiskSummary {
  current_score: number;
  risk_level: string;
  previous_score: number | null;
  change: number | null;
  trend: 'increasing' | 'stable' | 'decreasing';
  last_updated: string;
}

export interface FinancialSummary {
  modeled_exposure: number;
  expected_annual_loss: number;
  breakdown: Record<string, number>;
  last_updated: string;
}

export interface PredictionSummary {
  forecast_30_day: number;
  trend: 'increasing' | 'stable' | 'decreasing';
  confidence: number;
  last_updated: string;
}

export interface AssetRiskSummary {
  asset_id: string;
  asset_name: string;
  risk_score: number;
  criticality: number;
  financial_exposure: number;
  predicted_risk: number | null;
  trend: string;
}

export interface TopRiskDrivers {
  driver_name: string;
  risk_contribution: number;
  category: string;
}

export interface ThreatSummary {
  threat_id: string;
  name: string;
  affected_assets: number;
  confidence: number;
  severity: string;
  trend: string;
}

export interface VulnerabilitySummary {
  vulnerability_id: string;
  name: string;
  severity: string;
  known_exploited: boolean;
  affected_assets: number;
  risk_contribution: number;
}

export interface RecommendationSummary {
  recommendation_id: string;
  action: string;
  asset_name: string | null;
  priority: string;
  estimated_risk_reduction: number;
  financial_exposure_reduction: number;
  urgency: string;
  status: string;
}

export interface BudgetSummary {
  recommended_budget: number;
  budget_used: number;
  budget_remaining: number;
  selected_investments: number;
  risk_before: number;
  risk_after: number;
  financial_exposure_before: number;
  financial_exposure_after: number;
  last_updated: string;
}

export interface ComplianceSummary {
  framework_name: string;
  coverage_percentage: number;
  compliant: number;
  partially_compliant: number;
  non_compliant: number;
  insufficient_evidence: number;
  open_gaps: number;
}

export interface DashboardAlert {
  id: string;
  title: string;
  reason: string;
  source_module: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  action_link: string | null;
  status: string;
  first_seen: string;
  last_seen: string;
}

export interface ExecutiveInsight {
  id: string;
  content: string;
  insight_type: string;
  generated_at: string;
}

export interface DataQuality {
  risk_engine: string;
  prediction: string;
  financial_model: string;
  compliance: string;
}

export interface ExecutiveDashboardData {
  organization_id: string;
  last_updated: string;
  risk: RiskSummary;
  financial: FinancialSummary | null;
  prediction: PredictionSummary | null;
  top_assets: AssetRiskSummary[];
  risk_drivers: TopRiskDrivers[];
  threats: ThreatSummary[];
  vulnerabilities: VulnerabilitySummary[];
  recommendations: RecommendationSummary[];
  budget: BudgetSummary | null;
  compliance: ComplianceSummary[];
  alerts: DashboardAlert[];
  insights: ExecutiveInsight[];
  data_quality: DataQuality;
}
