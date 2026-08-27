export interface RecommendationEvidence {
  source: string;
  detail: string;
  severity: string;
}

export interface RecommendationMetadata {
  rationale: string;
  risk_driver: string;
  urgency: string;
  expected_financial_benefit?: number;
  implementation_effort: string;
  confidence: number;
  evidence: RecommendationEvidence[];
}

export interface Recommendation {
  id: string;
  organization_id: string;
  asset_id?: string;
  title: string;
  description?: string;
  priority: string;
  estimated_cost?: number;
  expected_risk_reduction?: number;
  status: string;
  metadata?: RecommendationMetadata;
  generated_at: string;
  accepted_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}
