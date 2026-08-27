import api from './api';
import type { 
  PaginatedThreatIntelligence, 
  ThreatIntelligenceRecord, 
  ThreatIntelligenceStats, 
  ThreatFilters,
  ThreatCorrelation
} from '../types/threatIntelligence';

export const threatIntelligenceService = {
  getThreats: async (filters: ThreatFilters = {}): Promise<PaginatedThreatIntelligence> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    return api.get<PaginatedThreatIntelligence>(`/api/v1/threat-intelligence?${params.toString()}`);
  },

  getThreat: async (id: string): Promise<ThreatIntelligenceRecord> => {
    return api.get<ThreatIntelligenceRecord>(`/api/v1/threat-intelligence/${id}`);
  },

  getThreatStats: async (): Promise<ThreatIntelligenceStats> => {
    return api.get<ThreatIntelligenceStats>('/api/v1/threat-intelligence/stats');
  },

  getAssetThreatIntelligence: async (assetId: string): Promise<ThreatCorrelation[]> => {
    return api.get<ThreatCorrelation[]>(`/api/v1/assets/${assetId}/threat-intelligence`);
  },
  
  getVulnerabilityThreatIntelligence: async (vulnerabilityId: string): Promise<ThreatCorrelation[]> => {
    return api.get<ThreatCorrelation[]>(`/api/v1/vulnerabilities/${vulnerabilityId}/threat-intelligence`);
  }
};
