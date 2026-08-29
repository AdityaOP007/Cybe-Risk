import React, { useState } from 'react';
import type {  AssetCreateRequest, Asset  } from "../../types/asset";
import { X } from 'lucide-react';

interface AssetFormProps {
  onClose: () => void;
  onSubmit: (data: AssetCreateRequest) => Promise<void>;
  initialData?: Asset;
  organizationId: string;
}

export const AssetForm: React.FC<AssetFormProps> = ({ onClose, onSubmit, initialData, organizationId }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<AssetCreateRequest>({
    organization_id: organizationId,
    name: initialData?.name || '',
    description: initialData?.description || '',
    asset_type: initialData?.asset_type || 'server',
    environment: initialData?.environment || 'production',
    criticality: initialData?.criticality || 50,
    business_value: initialData?.business_value || 0,
    owner: initialData?.owner || '',
    department: initialData?.department || '',
    hostname: initialData?.hostname || '',
    ip_address: initialData?.ip_address || '',
    technology: initialData?.technology || '',
    internet_exposed: initialData?.internet_exposed || false,
    status: initialData?.status || 'active',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      setFormData(prev => ({ ...prev, [name]: (e.target as HTMLInputElement).checked }));
    } else if (type === 'number') {
      setFormData(prev => ({ ...prev, [name]: Number(value) }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save asset.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto overflow-x-hidden bg-slate-950/80 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl rounded-xl border border-slate-700 bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-700 px-6 py-4">
          <h3 className="text-xl font-semibold text-white">
            {initialData ? 'Edit Asset' : 'Create Asset'}
          </h3>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6">
          {error && (
            <div className="mb-6 rounded-lg bg-red-500/10 p-4 text-sm text-red-400 border border-red-500/20">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="col-span-2">
                <label className="mb-1 block text-sm font-medium text-slate-300">Name *</label>
                <input
                  type="text"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">Asset Type *</label>
                <select
                  name="asset_type"
                  value={formData.asset_type}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="server">Server</option>
                  <option value="database">Database</option>
                  <option value="application">Application</option>
                  <option value="endpoint">Endpoint</option>
                  <option value="network_device">Network Device</option>
                  <option value="cloud_resource">Cloud Resource</option>
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">Environment *</label>
                <select
                  name="environment"
                  value={formData.environment}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                  <option value="testing">Testing</option>
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">Criticality (0-100)</label>
                <input
                  type="number"
                  name="criticality"
                  min="0"
                  max="100"
                  value={formData.criticality}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">Business Value ($)</label>
                <input
                  type="number"
                  name="business_value"
                  min="0"
                  value={formData.business_value}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">Hostname</label>
                <input
                  type="text"
                  name="hostname"
                  value={formData.hostname}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">IP Address</label>
                <input
                  type="text"
                  name="ip_address"
                  value={formData.ip_address}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">Owner</label>
                <input
                  type="text"
                  name="owner"
                  value={formData.owner}
                  onChange={handleChange}
                  className="block w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="flex items-center mt-6">
                <input
                  type="checkbox"
                  id="internet_exposed"
                  name="internet_exposed"
                  checked={formData.internet_exposed}
                  onChange={handleChange}
                  className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-indigo-500 focus:ring-indigo-500 focus:ring-offset-slate-900"
                />
                <label htmlFor="internet_exposed" className="ml-2 block text-sm text-slate-300">
                  Internet Exposed
                </label>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-slate-700 pt-6">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="rounded-lg bg-indigo-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-600 transition-colors disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Save Asset'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
