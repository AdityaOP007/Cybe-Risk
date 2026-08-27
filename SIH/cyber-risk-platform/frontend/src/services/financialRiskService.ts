import api from './api';
import {
  FinancialRiskAssessment,
  FinancialBreakdown,
  FinancialAssumption,
  OrganizationFinancialRiskSummary
} from '../types/financialRisk';

const API_PREFIX = '/financial-risk';

export const financialRiskService = {
  // Asset Endpoints
  calculateAssetFinancialRisk: async (assetId: string): Promise<FinancialRiskAssessment> => {
    const response = await api.post(`${API_PREFIX}/assets/${assetId}/calculate`);
    return response.data;
  },

  getAssetFinancialRisk: async (assetId: string): Promise<FinancialRiskAssessment> => {
    const response = await api.get(`${API_PREFIX}/assets/${assetId}`);
    return response.data;
  },

  getAssetFinancialRiskHistory: async (assetId: string): Promise<FinancialRiskAssessment[]> => {
    const response = await api.get(`${API_PREFIX}/assets/${assetId}/history`);
    return response.data;
  },

  getAssetFinancialBreakdown: async (assetId: string): Promise<FinancialBreakdown> => {
    const response = await api.get(`${API_PREFIX}/assets/${assetId}/breakdown`);
    return response.data;
  },

  getAssetAssumptions: async (assetId: string): Promise<FinancialAssumption[]> => {
    const response = await api.get(`${API_PREFIX}/assets/${assetId}/assumptions`);
    return response.data;
  },

  // Organization Endpoints
  calculateOrganizationFinancialRisk: async (organizationId: string): Promise<{ status: string; message: string }> => {
    const response = await api.post(`${API_PREFIX}/organizations/${organizationId}/calculate`);
    return response.data;
  },

  getOrganizationFinancialRisk: async (organizationId: string): Promise<OrganizationFinancialRiskSummary> => {
    const response = await api.get(`${API_PREFIX}/organizations/${organizationId}`);
    return response.data;
  },
};

export default financialRiskService;
