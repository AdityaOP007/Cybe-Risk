export interface FinancialAssumption {
  id: string;
  organization_id: string;
  category: string;
  name: string;
  value: number;
  unit: string | null;
  currency: string;
  source: string;
  confidence: number;
  effective_from: string;
  effective_until: string | null;
  created_at: string;
  updated_at: string;
}

export interface FinancialBreakdown {
  direct_loss: number;
  data_loss: number;
  business_interruption_loss: number;
  recovery_loss: number;
  customer_impact: number;
  third_party_impact: number;
  regulatory_legal_exposure: number;
  fraud_loss: number;
  reputation_revenue_impact: number;
}

export interface FinancialRiskAssessment {
  id: string;
  organization_id: string;
  asset_id: string;
  risk_score_id: string;
  
  potential_loss: number;
  expected_loss: number;
  annualized_expected_loss: number;
  
  direct_loss: number;
  data_loss: number;
  business_interruption_loss: number;
  recovery_loss: number;
  customer_impact: number;
  third_party_impact: number;
  regulatory_legal_exposure: number;
  fraud_loss: number;
  reputation_revenue_impact: number;
  
  confidence: number;
  data_completeness: number;
  currency: string;
  calculation_version: string;
  
  assumptions_snapshot: Record<string, any> | null;
  metadata: Record<string, any> | null;
  
  calculated_at: string;
  created_at: string;
}

export interface OrganizationFinancialRiskSummary {
  organization_id: string;
  currency: string;
  total_potential_loss: number;
  total_expected_annual_loss: number;
  top_financial_risk_assets: FinancialRiskAssessment[];
  aggregate_breakdown: FinancialBreakdown;
  average_confidence: number;
}
