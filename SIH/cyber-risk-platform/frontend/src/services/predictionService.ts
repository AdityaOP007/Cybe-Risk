import api from './api';
import type { 
  AssetRiskForecastResponse,
  PredictionBulkResult,
  PredictionModel
 } from "../types/prediction";

const API_PREFIX = '/api/v1/predictions';

export const predictionService = {
  calculateAssetPrediction: async (assetId: string): Promise<AssetRiskForecastResponse> => {
    return api.post<AssetRiskForecastResponse>(`${API_PREFIX}/assets/${assetId}/calculate`);
  },

  getAssetPrediction: async (assetId: string): Promise<AssetRiskForecastResponse> => {
    return api.get<AssetRiskForecastResponse>(`${API_PREFIX}/assets/${assetId}`);
  },

  calculateAllPredictions: async (organizationId: string): Promise<PredictionBulkResult> => {
    return api.post<PredictionBulkResult>(`${API_PREFIX}/organizations/${organizationId}/calculate-all`);
  },

  getModels: async (): Promise<PredictionModel[]> => {
    return api.get<PredictionModel[]>(`${API_PREFIX}/models`);
  }
};

export default predictionService;
