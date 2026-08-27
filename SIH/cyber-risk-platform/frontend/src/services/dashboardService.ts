import api from './api';
import { ExecutiveDashboardData } from '../types/dashboard';

export const getExecutiveDashboard = async (): Promise<ExecutiveDashboardData> => {
  const response = await api.get('/dashboard/executive');
  return response.data;
};

export const acknowledgeAlert = async (alertId: string): Promise<void> => {
  await api.post(`/dashboard/alerts/${alertId}/acknowledge`);
};

export const resolveAlert = async (alertId: string): Promise<void> => {
  await api.post(`/dashboard/alerts/${alertId}/resolve`);
};
