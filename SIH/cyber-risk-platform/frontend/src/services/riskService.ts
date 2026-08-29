import api from './api';
import type { RiskScore, RiskTrendResponse } from '../types/risk';

export const riskService = {
  calculateAssetRisk: async (assetId: string): Promise<RiskScore> => {
    return api.post<RiskScore>(`/api/v1/risk/calculate/asset/${assetId}`);
  },

  calculateOrganizationRisk: async (orgId: string): Promise<RiskScore> => {
    return api.post<RiskScore>(`/api/v1/risk/calculate/organization/${orgId}`);
  },

  getAssetRiskTrend: async (assetId: string): Promise<RiskTrendResponse> => {
    return api.get<RiskTrendResponse>(`/api/v1/risk/assets/${assetId}`);
  },

  getOrganizationRiskTrend: async (orgId: string): Promise<RiskTrendResponse> => {
    return api.get<RiskTrendResponse>(`/api/v1/risk/organizations/${orgId}`);
  }
};
