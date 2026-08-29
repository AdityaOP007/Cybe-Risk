import React from 'react';
import type {  AssetRiskSummary  } from "../../types/dashboard";
import { TrendingUp, Minus } from 'lucide-react';

interface TopRiskAssetsProps {
  assets: AssetRiskSummary[];
}

export const TopRiskAssets: React.FC<TopRiskAssetsProps> = ({ assets }) => {
  const formatCurrency = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(1)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)}L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  return (
    <div className="bg-[#0f172a] rounded-xl border border-gray-800 shadow-md">
      <div className="p-5 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-white">Priority Exposure (Top Assets)</h3>
      </div>
      <div className="p-0 overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-400">
          <thead className="text-xs text-gray-500 uppercase bg-slate-800/50 border-b border-gray-800">
            <tr>
              <th className="px-5 py-3 font-medium">Asset Name</th>
              <th className="px-5 py-3 font-medium text-right">Risk Score</th>
              <th className="px-5 py-3 font-medium text-right">Financial Exposure</th>
              <th className="px-5 py-3 font-medium text-center">Trend</th>
            </tr>
          </thead>
          <tbody>
            {assets.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-gray-500">
                  No assets currently assessed for risk.
                </td>
              </tr>
            ) : (
              assets.map((asset) => (
                <tr key={asset.asset_id} className="border-b border-gray-800/50 hover:bg-slate-800/30">
                  <td className="px-5 py-4 font-medium text-gray-300">{asset.asset_name}</td>
                  <td className="px-5 py-4 text-right">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      asset.risk_score > 80 ? 'bg-red-500/20 text-red-400' :
                      asset.risk_score > 60 ? 'bg-orange-500/20 text-orange-400' :
                      'bg-emerald-500/20 text-emerald-400'
                    }`}>
                      {asset.risk_score.toFixed(0)}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right text-rose-400 font-medium">
                    {formatCurrency(asset.financial_exposure)}
                  </td>
                  <td className="px-5 py-4 text-center">
                    {asset.trend === 'increasing' ? (
                      <TrendingUp className="h-4 w-4 text-red-500 inline" />
                    ) : (
                      <Minus className="h-4 w-4 text-gray-500 inline" />
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
