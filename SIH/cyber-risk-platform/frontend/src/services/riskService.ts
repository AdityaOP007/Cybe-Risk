import { api } from './api';
import type { RiskScore, RiskTrendResponse } from '../types/risk';

export const riskService = {
  calculateAssetRisk: async (assetId: string): Promise<RiskScore> => {
    const response = await api.post<RiskScore>(`/risk/calculate/asset/${assetId}`);
    return response.data;
  },

  calculateOrganizationRisk: async (orgId: string): Promise<RiskScore> => {
    const response = await api.post<RiskScore>(`/risk/calculate/organization/${orgId}`);
    return response.data;
  },

  getAssetRiskTrend: async (assetId: string): Promise<RiskTrendResponse> => {
    const response = await api.get<RiskTrendResponse>(`/risk/assets/${assetId}`);
    return response.data;
  },

  getOrganizationRiskTrend: async (orgId: string): Promise<RiskTrendResponse> => {
    const response = await api.get<RiskTrendResponse>(`/risk/organizations/${orgId}`);
    return response.data;
  }
};
