import React from 'react';
import { Link } from 'react-router-dom';
import type {  Asset  } from "../../types/asset";
import { CriticalityBadge, EnvironmentBadge, ExposureBadge, StatusBadge } from './Badges';
import { ChevronLeft, ChevronRight, Eye, Edit, Trash } from 'lucide-react';

interface AssetTableProps {
  assets: Asset[];
  loading: boolean;
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onRetire: (id: string) => void;
}

export const AssetTable: React.FC<AssetTableProps> = ({ 
  assets, 
  loading, 
  page, 
  totalPages, 
  onPageChange,
  onRetire
}) => {
  return (
    <div className="w-full flex flex-col">
      <div className="overflow-x-auto rounded-lg border border-slate-700 bg-slate-900 shadow-xl">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-800 text-xs uppercase text-slate-400">
            <tr>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider">Asset</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider">Type</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider">Environment</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider">Criticality</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider hidden md:table-cell">Value</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider hidden lg:table-cell">Exposure</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider hidden xl:table-cell">Owner</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider">Status</th>
              <th scope="col" className="px-6 py-4 font-medium tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {loading ? (
              <tr>
                <td colSpan={9} className="px-6 py-12 text-center text-slate-500">
                  <div className="flex justify-center items-center">
                    <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="ml-3">Loading assets...</span>
                  </div>
                </td>
              </tr>
            ) : assets.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-12 text-center text-slate-500">
                  No assets found. Try adjusting your search or filters.
                </td>
              </tr>
            ) : (
              assets.map((asset) => (
                <tr key={asset.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <Link to={`/assets/${asset.id}`} className="font-semibold text-white hover:text-indigo-400">
                        {asset.name}
                      </Link>
                      {asset.hostname && (
                        <span className="text-xs text-slate-500 mt-0.5">{asset.hostname}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap capitalize">
                    {asset.asset_type.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <EnvironmentBadge env={asset.environment} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <CriticalityBadge criticality={asset.criticality} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap hidden md:table-cell">
                    ${(asset.business_value || 0).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap hidden lg:table-cell">
                    <ExposureBadge exposed={asset.internet_exposed} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap hidden xl:table-cell text-slate-400">
                    {asset.owner || '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={asset.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-3">
                      <Link to={`/assets/${asset.id}`} className="text-slate-400 hover:text-white" title="View details">
                        <Eye size={18} />
                      </Link>
                      <button className="text-slate-400 hover:text-indigo-400" title="Edit asset">
                        <Edit size={18} />
                      </button>
                      {asset.status !== 'retired' && (
                        <button 
                          onClick={() => {
                            if (confirm('Are you sure you want to retire this asset?')) {
                              onRetire(asset.id);
                            }
                          }}
                          className="text-slate-400 hover:text-red-400" 
                          title="Retire asset"
                        >
                          <Trash size={18} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {!loading && assets.length > 0 && (
        <div className="flex items-center justify-between px-4 py-4 mt-4 bg-slate-900 rounded-lg border border-slate-700">
          <div className="text-sm text-slate-400">
            Showing page <span className="font-medium text-white">{page}</span> of <span className="font-medium text-white">{totalPages}</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-3 py-1.5 flex items-center justify-center gap-1 text-sm rounded bg-slate-800 text-white border border-slate-700 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={16} /> Previous
            </button>
            <button
              onClick={() => onPageChange(Math.min(totalPages, page + 1))}
              disabled={page === totalPages || totalPages === 0}
              className="px-3 py-1.5 flex items-center justify-center gap-1 text-sm rounded bg-slate-800 text-white border border-slate-700 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
