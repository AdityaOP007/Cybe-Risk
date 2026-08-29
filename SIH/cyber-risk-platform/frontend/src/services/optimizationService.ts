import api from './api';
import type { 
  OptimizationRunRequest, 
  OptimizationRun, 
  CybersecurityInvestment 
} from '../types/optimization';

const API_PREFIX = '/api/v1/optimization';

export const optimizationService = {
  getInvestments: async (): Promise<CybersecurityInvestment[]> => {
    return api.get<CybersecurityInvestment[]>(`${API_PREFIX}/investments`);
  },

  runOptimization: async (request: OptimizationRunRequest): Promise<OptimizationRun> => {
    return api.post<OptimizationRun>(`${API_PREFIX}/run`, request);
  },

  getOptimizationRuns: async (): Promise<OptimizationRun[]> => {
    return api.get<OptimizationRun[]>(`${API_PREFIX}/runs`);
  }
};

export default optimizationService;
