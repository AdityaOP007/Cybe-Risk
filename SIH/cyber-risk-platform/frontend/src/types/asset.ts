export type AssetType = 'server' | 'database' | 'application' | 'endpoint' | 'network_device' | 'cloud_resource' | 'api' | 'payment_system' | 'storage' | 'container' | 'virtual_machine' | 'other';
export type AssetEnvironment = 'production' | 'staging' | 'development' | 'testing';
export type AssetStatus = 'active' | 'inactive' | 'maintenance' | 'retired';

export interface Asset {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  asset_type: AssetType | string;
  environment: AssetEnvironment | string;
  criticality: number; // 0-100
  business_value: number;
  owner?: string;
  department?: string;
  hostname?: string;
  ip_address?: string;
  operating_system?: string;
  technology?: string;
  internet_exposed: boolean;
  status: AssetStatus | string;
  created_at: string;
  updated_at: string;
}

export interface AssetCreateRequest {
  organization_id: string;
  name: string;
  description?: string;
  asset_type: string;
  environment: string;
  criticality: number;
  business_value: number;
  owner?: string;
  department?: string;
  hostname?: string;
  ip_address?: string;
  operating_system?: string;
  technology?: string;
  internet_exposed: boolean;
  status: string;
}

export type AssetUpdateRequest = Partial<Omit<AssetCreateRequest, 'organization_id'>>;

export interface PaginatedAssets {
  items: Asset[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface AssetFilters {
  search?: string;
  organization_id?: string;
  asset_type?: string;
  environment?: string;
  status?: string;
  internet_exposed?: boolean;
  criticality_min?: number;
  criticality_max?: number;
  department?: string;
  owner?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export interface AssetPosture {
  asset_id: string;
  asset_name: string;
  criticality: number;
  internet_exposed: boolean;
  open_vulnerabilities: number;
  critical_vulnerabilities: number;
  recent_telemetry_events: number;
}
