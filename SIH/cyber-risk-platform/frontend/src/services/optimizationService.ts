import api from './api';
import type { 
  OptimizationRunRequest, 
  OptimizationRun, 
  CybersecurityInvestment 
} from '../types/optimization';

const API_PREFIX = '/optimization';

export const optimizationService = {
  getInvestments: async (): Promise<CybersecurityInvestment[]> => {
    const response = await api.get(`${API_PREFIX}/investments`);
    return response.data;
  },

  runOptimization: async (request: OptimizationRunRequest): Promise<OptimizationRun> => {
    const response = await api.post(`${API_PREFIX}/run`, request);
    return response.data;
  },

  getOptimizationRuns: async (): Promise<OptimizationRun[]> => {
    const response = await api.get(`${API_PREFIX}/runs`);
    return response.data;
  }
};

export default optimizationService;
