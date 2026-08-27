import api from './api';
import type { TelemetryEvent, PaginatedTelemetry, TelemetryStats, TelemetryEventFilters } from '../types/telemetry';

export const telemetryService = {
  getTelemetryEvents: async (filters: TelemetryEventFilters = {}): Promise<PaginatedTelemetry> => {
    // Build query params
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    return api.get<PaginatedTelemetry>(`/api/v1/telemetry/events?${params.toString()}`);
  },

  getTelemetryEvent: async (id: string): Promise<TelemetryEvent> => {
    return api.get<TelemetryEvent>(`/api/v1/telemetry/events/${id}`);
  },

  getTelemetryStats: async (organizationId?: string): Promise<TelemetryStats> => {
    const url = organizationId 
      ? `/api/v1/telemetry/stats?organization_id=${organizationId}` 
      : `/api/v1/telemetry/stats`;
    return api.get<TelemetryStats>(url);
  },

  getRecentTelemetry: async (organizationId?: string, limit: number = 20): Promise<TelemetryEvent[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (organizationId) {
      params.append('organization_id', organizationId);
    }
    return api.get<TelemetryEvent[]>(`/api/v1/telemetry/events/recent?${params.toString()}`);
  },

  getAssetTelemetry: async (assetId: string, page: number = 1, pageSize: number = 10): Promise<PaginatedTelemetry> => {
    return api.get<PaginatedTelemetry>(`/api/v1/telemetry/events?asset_id=${assetId}&page=${page}&page_size=${pageSize}`);
  }
};
