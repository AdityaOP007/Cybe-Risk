export interface OptimizationWeights {
  risk_weight: number;
  financial_weight: number;
  criticality_weight: number;
  urgency_weight: number;
  confidence_weight: number;
}

export interface OptimizationRunRequest {
  budget: number;
  currency: string;
  horizon_months: number;
  objective: string;
  weights: OptimizationWeights;
}

export interface CybersecurityInvestment {
  id: string;
  organization_id: string;
  title: string;
  description?: string;
  category?: string;
  cost: number;
  currency: string;
  cost_type: string;
  annualized_cost?: number;
  implementation_effort?: string;
  risk_reduction?: number;
  financial_reduction?: number;
  confidence?: number;
  priority?: string;
  urgency?: string;
  mandatory: boolean;
  status: string;
}

export interface OptimizationPortfolio {
  id: string;
  optimization_run_id: string;
  selected_investments: string[];
  total_cost: number;
  risk_reduction?: number;
  financial_reduction?: number;
  metadata?: {
    explanation?: string;
  };
}

export interface OptimizationRun {
  id: string;
  budget: number;
  currency: string;
  horizon_months: number;
  objective: string;
  optimization_status: string;
  total_cost: number;
  remaining_budget: number;
  risk_before?: number;
  risk_after?: number;
  risk_reduction?: number;
  financial_before?: number;
  financial_after?: number;
  financial_reduction?: number;
  portfolios: OptimizationPortfolio[];
  created_at: string;
}
