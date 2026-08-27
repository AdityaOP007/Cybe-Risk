/**
 * Centralized API client.
 *
 * All backend communication goes through this module.
 * The base URL is loaded from the VITE_API_BASE_URL environment variable.
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
}

/**
 * Generic fetch wrapper with error handling.
 * Prevents leaking raw error details to the UI.
 */
async function request<T>(endpoint: string): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/v1/health');
}

export default {
  checkHealth,
};
