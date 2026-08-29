import api from './api';
import type {  ExecutiveDashboardData  } from "../types/dashboard";

export const getExecutiveDashboard = async (): Promise<ExecutiveDashboardData> => {
  return api.get<ExecutiveDashboardData>('/api/v1/dashboard/executive');
};

export const acknowledgeAlert = async (alertId: string): Promise<void> => {
  await api.post(`/api/v1/dashboard/alerts/${alertId}/acknowledge`);
};

export const resolveAlert = async (alertId: string): Promise<void> => {
  await api.post(`/api/v1/dashboard/alerts/${alertId}/resolve`);
};
