import React, { useState, useEffect, useCallback } from 'react';
import { assetService } from '../services/assetService';
import api from '../services/api';
import { Asset, AssetFilters as FilterType, AssetCreateRequest, PaginatedAssets } from '../types/asset';
import { AssetTable } from '../components/assets/AssetTable';
import { AssetSearch } from '../components/assets/AssetSearch';
import { AssetFilters } from '../components/assets/AssetFilters';
import { AssetForm } from '../components/assets/AssetForm';
import { Plus } from 'lucide-react';

export const Assets: React.FC = () => {
  const [assetsData, setAssetsData] = useState<PaginatedAssets>({
    items: [],
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [filters, setFilters] = useState<FilterType>({
    page: 1,
    page_size: 20,
    sort_by: 'created_at',
    sort_order: 'desc'
  });

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [orgId, setOrgId] = useState<string>('');

  const fetchAssets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await assetService.getAssets(filters);
      setAssetsData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch assets.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  // Fetch the first organization ID just so we can create assets
  useEffect(() => {
    const fetchOrg = async () => {
      try {
        const response = await api.get<{ items: { id: string }[] }>('/api/v1/organizations/');
        if (response.items && response.items.length > 0) {
          setOrgId(response.items[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch organization for asset creation', err);
      }
    };
    fetchOrg();
  }, []);

  const handleSearch = (search: string) => {
    setFilters(prev => ({
      ...prev,
      search: search || undefined,
      page: 1
    }));
  };

  const handleFilterChange = (newFilters: FilterType) => {
    setFilters(newFilters);
  };

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  const handleRetire = async (id: string) => {
    try {
      await assetService.retireAsset(id);
      fetchAssets();
    } catch (err: any) {
      alert(`Failed to retire asset: ${err.message}`);
    }
  };

  const handleCreateAsset = async (data: AssetCreateRequest) => {
    await assetService.createAsset(data);
    fetchAssets();
  };

  return (
    <div className="w-full max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-white sm:truncate sm:text-3xl sm:tracking-tight">
            Asset Management
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            A comprehensive inventory of your organization's devices, applications, and resources.
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button
            onClick={() => setIsFormOpen(true)}
            disabled={!orgId}
            className="inline-flex items-center rounded-md bg-indigo-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 disabled:opacity-50 transition-colors"
          >
            <Plus className="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
            New Asset
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-md bg-red-500/10 p-4 border border-red-500/20">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-400">Error</h3>
              <div className="mt-2 text-sm text-red-400/80">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-slate-900/50 rounded-xl p-4 mb-6 border border-slate-700/50 backdrop-blur-sm">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <AssetSearch initialValue={filters.search} onSearch={handleSearch} />
          <div className="w-full md:w-auto overflow-x-auto">
            <AssetFilters filters={filters} onChange={handleFilterChange} />
          </div>
        </div>
      </div>

      <AssetTable 
        assets={assetsData.items} 
        loading={loading} 
        page={assetsData.page}
        totalPages={assetsData.total_pages}
        onPageChange={handlePageChange}
        onRetire={handleRetire}
      />

      {isFormOpen && (
        <AssetForm 
          organizationId={orgId}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleCreateAsset}
        />
      )}
    </div>
  );
};
