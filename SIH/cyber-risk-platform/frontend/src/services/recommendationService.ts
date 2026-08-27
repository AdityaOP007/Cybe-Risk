import api from './api';
import { Recommendation } from '../types/recommendation';

const API_PREFIX = '/recommendations';

export const recommendationService = {
  generateRecommendations: async (): Promise<Recommendation[]> => {
    const response = await api.post(`${API_PREFIX}/generate`);
    return response.data;
  },

  getRecommendations: async (): Promise<Recommendation[]> => {
    const response = await api.get(`${API_PREFIX}/`);
    return response.data;
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
    
    const response = await api.patch(`${API_PREFIX}/${id}`, updateData);
    return response.data;
  }
};

export default recommendationService;
