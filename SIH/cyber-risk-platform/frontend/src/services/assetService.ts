import api from './api';
import { Asset, AssetCreateRequest, AssetUpdateRequest, PaginatedAssets, AssetFilters, AssetPosture } from '../types/asset';

export const assetService = {
  getAssets: async (filters?: AssetFilters): Promise<PaginatedAssets> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    return api.get(`/api/v1/assets/?${params.toString()}`);
  },

  getAsset: async (id: string): Promise<Asset> => {
    return api.get(`/api/v1/assets/${id}`);
  },

  createAsset: async (asset: AssetCreateRequest): Promise<Asset> => {
    return api.post('/api/v1/assets/', asset);
  },

  updateAsset: async (id: string, asset: AssetUpdateRequest): Promise<Asset> => {
    return api.put(`/api/v1/assets/${id}`, asset);
  },

  retireAsset: async (id: string): Promise<{ message: string; asset_id: string }> => {
    return api.post(`/api/v1/assets/${id}/retire`);
  },

  getAssetPosture: async (id: string): Promise<AssetPosture> => {
    return api.get(`/api/v1/assets/${id}/posture`);
  },

  getAssetVulnerabilities: async (id: string, page = 1, pageSize = 50): Promise<any[]> => {
    return api.get(`/api/v1/assets/${id}/vulnerabilities?page=${page}&page_size=${pageSize}`);
  },

  getAssetTelemetry: async (id: string, page = 1, pageSize = 50): Promise<any[]> => {
    return api.get(`/api/v1/assets/${id}/telemetry?page=${page}&page_size=${pageSize}`);
  },
};
