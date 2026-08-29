import api from './api';
import type { 
  FinancialRiskAssessment,
  FinancialBreakdown,
  FinancialAssumption,
  OrganizationFinancialRiskSummary
 } from "../types/financialRisk";

const API_PREFIX = '/api/v1/financial-risk';

export const financialRiskService = {
  // Asset Endpoints
  calculateAssetFinancialRisk: async (assetId: string): Promise<FinancialRiskAssessment> => {
    return api.post<FinancialRiskAssessment>(`${API_PREFIX}/assets/${assetId}/calculate`);
  },

  getAssetFinancialRisk: async (assetId: string): Promise<FinancialRiskAssessment> => {
    return api.get<FinancialRiskAssessment>(`${API_PREFIX}/assets/${assetId}`);
  },

  getAssetFinancialRiskHistory: async (assetId: string): Promise<FinancialRiskAssessment[]> => {
    return api.get<FinancialRiskAssessment[]>(`${API_PREFIX}/assets/${assetId}/history`);
  },

  getAssetFinancialBreakdown: async (assetId: string): Promise<FinancialBreakdown> => {
    return api.get<FinancialBreakdown>(`${API_PREFIX}/assets/${assetId}/breakdown`);
  },

  getAssetAssumptions: async (assetId: string): Promise<FinancialAssumption[]> => {
    return api.get<FinancialAssumption[]>(`${API_PREFIX}/assets/${assetId}/assumptions`);
  },

  // Organization Endpoints
  calculateOrganizationFinancialRisk: async (organizationId: string): Promise<{ status: string; message: string }> => {
    return api.post<{ status: string; message: string }>(`${API_PREFIX}/organizations/${organizationId}/calculate`);
  },

  getOrganizationFinancialRisk: async (organizationId: string): Promise<OrganizationFinancialRiskSummary> => {
    return api.get<OrganizationFinancialRiskSummary>(`${API_PREFIX}/organizations/${organizationId}`);
  },
};

export default financialRiskService;
