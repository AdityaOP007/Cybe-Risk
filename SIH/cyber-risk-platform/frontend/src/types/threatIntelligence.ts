export interface ThreatIndicator {
  id: string;
  threat_record_id: string;
  indicator_type: string;
  value: string;
  confidence: number | null;
  source: string | null;
  active: boolean;
  first_seen_at: string | null;
  last_seen_at: string | null;
  metadata_data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ThreatIntelligenceRecord {
  id: string;
  source: string;
  source_record_id: string;
  intelligence_type: 'vulnerability' | 'malware' | 'campaign' | 'actor' | string;
  title: string;
  description: string | null;
  severity: 'informational' | 'low' | 'medium' | 'high' | 'critical';
  confidence: number | null;
  external_reference: string | null;
  published_at: string | null;
  first_seen_at: string | null;
  last_seen_at: string | null;
  known_exploited: boolean;
  raw_data: Record<string, any>;
  normalized_data: Record<string, any>;
  indicators: ThreatIndicator[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedThreatIntelligence {
  items: ThreatIntelligenceRecord[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface ThreatCorrelation {
  id: string;
  organization_id: string;
  threat_record_id: string;
  asset_id: string | null;
  vulnerability_id: string | null;
  correlation_type: string;
  confidence: number;
  reason: string;
  detected_at: string;
  metadata_data: Record<string, any>;
  threat_record?: ThreatIntelligenceRecord;
}

export interface ThreatIntelligenceStats {
  total_threats: number;
  known_exploited: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  informational: number;
  indicators: number;
  by_source: Record<string, number>;
  by_intelligence_type: Record<string, number>;
}

export interface ThreatFilters {
  search?: string;
  severity?: string;
  source?: string;
  intelligence_type?: string;
  known_exploited?: boolean;
  page?: number;
  page_size?: number;
}
