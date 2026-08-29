import React from 'react';
import type {  AssetFilters as FilterType  } from "../../types/asset";

interface AssetFiltersProps {
  filters: FilterType;
  onChange: (filters: FilterType) => void;
}

export const AssetFilters: React.FC<AssetFiltersProps> = ({ filters, onChange }) => {
  const handleChange = (key: keyof FilterType, value: string | undefined) => {
    onChange({
      ...filters,
      [key]: value === '' ? undefined : value,
      page: 1, // Reset to first page on filter change
    });
  };

  return (
    <div className="flex flex-wrap items-center gap-3 w-full">
      <select
        className="block w-full sm:w-auto pl-3 pr-10 py-2 text-sm border border-slate-700 rounded-lg bg-slate-900 text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
        value={filters.asset_type || ''}
        onChange={(e) => handleChange('asset_type', e.target.value)}
      >
        <option value="">All Types</option>
        <option value="server">Server</option>
        <option value="database">Database</option>
        <option value="application">Application</option>
        <option value="network_device">Network Device</option>
        <option value="payment_system">Payment System</option>
      </select>

      <select
        className="block w-full sm:w-auto pl-3 pr-10 py-2 text-sm border border-slate-700 rounded-lg bg-slate-900 text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
        value={filters.environment || ''}
        onChange={(e) => handleChange('environment', e.target.value)}
      >
        <option value="">All Environments</option>
        <option value="production">Production</option>
        <option value="staging">Staging</option>
        <option value="development">Development</option>
      </select>

      <select
        className="block w-full sm:w-auto pl-3 pr-10 py-2 text-sm border border-slate-700 rounded-lg bg-slate-900 text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
        value={filters.status || ''}
        onChange={(e) => handleChange('status', e.target.value)}
      >
        <option value="">All Statuses</option>
        <option value="active">Active</option>
        <option value="maintenance">Maintenance</option>
        <option value="retired">Retired</option>
      </select>
      
      {(filters.asset_type || filters.environment || filters.status) && (
        <button
          onClick={() => onChange({ page: 1, page_size: filters.page_size })}
          className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          Clear Filters
        </button>
      )}
    </div>
  );
};
