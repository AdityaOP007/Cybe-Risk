import api from './api';
import {
  AssetRiskForecastResponse,
  PredictionBulkResult,
  PredictionModel
} from '../types/prediction';

const API_PREFIX = '/predictions';

export const predictionService = {
  calculateAssetPrediction: async (assetId: string): Promise<AssetRiskForecastResponse> => {
    const response = await api.post(`${API_PREFIX}/assets/${assetId}/calculate`);
    return response.data;
  },

  getAssetPrediction: async (assetId: string): Promise<AssetRiskForecastResponse> => {
    const response = await api.get(`${API_PREFIX}/assets/${assetId}`);
    return response.data;
  },

  calculateAllPredictions: async (organizationId: string): Promise<PredictionBulkResult> => {
    const response = await api.post(`${API_PREFIX}/organizations/${organizationId}/calculate-all`);
    return response.data;
  },

  getModels: async (): Promise<PredictionModel[]> => {
    const response = await api.get(`${API_PREFIX}/models`);
    return response.data;
  }
};

export default predictionService;
