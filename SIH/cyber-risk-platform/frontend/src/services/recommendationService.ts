import api from './api';
import type {  Recommendation  } from "../types/recommendation";

const API_PREFIX = '/api/v1/recommendations';

export const recommendationService = {
  generateRecommendations: async (): Promise<Recommendation[]> => {
    return api.post<Recommendation[]>(`${API_PREFIX}/generate`);
  },

  getRecommendations: async (): Promise<Recommendation[]> => {
    return api.get<Recommendation[]>(`${API_PREFIX}/`);
  },

  updateRecommendationStatus: async (
    id: string, 
    status: 'accepted' | 'completed' | 'rejected'
  ): Promise<Recommendation> => {
    const updateData: any = { status };
    if (status === 'accepted') {
      updateData.accepted_at = new Date().toISOString();
    } else if (status === 'completed') {
      updateData.completed_at = new Date().toISOString();
    }
    
    return api.patch<Recommendation>(`${API_PREFIX}/${id}`, updateData);
  }
};

export default recommendationService;
