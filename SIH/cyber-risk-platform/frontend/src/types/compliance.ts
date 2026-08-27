export interface ComplianceFramework {
  id: string;
  name: string;
  version: string | null;
  jurisdiction: string | null;
  effective_date: string | null;
  source_reference: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface FrameworkAssessmentSummary {
  framework_id: string;
  framework_name: string;
  framework_version: string | null;
  applicable_requirements: number;
  compliant: number;
  partially_compliant: number;
  non_compliant: number;
  insufficient_evidence: number;
  not_assessed: number;
  not_applicable: number;
  exceptions: number;
  coverage_percentage: number;
  evidence_coverage: number;
  overall_confidence: number;
  last_assessed: string | null;
}

export interface ComplianceGap {
  id: string;
  organization_id: string;
  framework_id: string;
  requirement_id: string;
  control_id: string | null;
  asset_id: string | null;
  gap_type: string;
  severity: string;
  risk_score: number | null;
  financial_exposure: number | null;
  description: string;
  evidence_gap: string | null;
  recommendation_id: string | null;
  status: string;
  created_at: string;
}

export interface CrosswalkMapping {
  requirement_id: string;
  title: string;
  mapping_type: string;
  coverage: number;
}

export interface CrosswalkResponse {
  [framework_name: string]: CrosswalkMapping[];
}
