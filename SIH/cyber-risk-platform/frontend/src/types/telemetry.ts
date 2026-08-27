export type TelemetrySeverity = 'informational' | 'low' | 'medium' | 'high' | 'critical';

export interface TelemetryEvent {
  id: string;
  organization_id: string;
  asset_id: string | null;
  source: string;
  event_type: string;
  severity: TelemetrySeverity;
  message: string | null;
  source_event_id: string | null;
  occurred_at: string;
  created_at: string;
  event_data: Record<string, any>;
}

export interface PaginatedTelemetry {
  items: TelemetryEvent[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface TelemetryStats {
  total_events: number;
  critical_events: number;
  high_events: number;
  medium_events: number;
  low_events: number;
  informational_events: number;
  by_source: Record<string, number>;
  by_event_type: Record<string, number>;
}

export interface TelemetryEventFilters {
  organization_id?: string;
  asset_id?: string;
  source?: string;
  event_type?: string;
  severity?: string;
  search?: string;
  from_time?: string;
  to_time?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}
