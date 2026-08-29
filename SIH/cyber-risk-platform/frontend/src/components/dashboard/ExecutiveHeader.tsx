import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { Activity, RefreshCw } from 'lucide-react';
import type {  DataQuality  } from "../../types/dashboard";

interface ExecutiveHeaderProps {
  organizationName: string;
  lastUpdated: string;
  dataQuality: DataQuality;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const ExecutiveHeader: React.FC<ExecutiveHeaderProps> = ({
  organizationName,
  lastUpdated,
  dataQuality,
  onRefresh,
  isRefreshing
}) => {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-gray-800">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20">
            <Activity className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Cyber Risk Command Center</h1>
            <p className="text-sm text-gray-400">{organizationName} Executive Decision Intelligence</p>
          </div>
        </div>
      </div>
      
      <div className="mt-4 md:mt-0 flex flex-col md:items-end gap-2">
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-400">
            Last Updated: <span className="text-gray-300 font-medium">{formatDistanceToNow(new Date(lastUpdated), { addSuffix: true })}</span>
          </span>
          <button 
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 rounded-lg bg-[#1e293b] px-4 py-2 text-sm font-medium text-white hover:bg-[#2d3b4e] disabled:opacity-50 transition-colors border border-gray-700"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} /> 
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        
        {/* Model Health / Data Quality Panel */}
        <div className="flex items-center gap-3 text-xs">
          <span className="text-gray-500 font-medium">Model Health:</span>
          <span className="flex items-center gap-1">
            <div className={`h-1.5 w-1.5 rounded-full ${dataQuality.risk_engine === 'Healthy' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
            <span className="text-gray-400">Risk</span>
          </span>
          <span className="flex items-center gap-1">
            <div className={`h-1.5 w-1.5 rounded-full ${dataQuality.financial_model === 'Healthy' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
            <span className="text-gray-400">Financial</span>
          </span>
          <span className="flex items-center gap-1">
            <div className={`h-1.5 w-1.5 rounded-full ${dataQuality.prediction === 'Healthy' ? 'bg-emerald-500' : 'bg-gray-500'}`}></div>
            <span className="text-gray-400">Prediction</span>
          </span>
          <span className="flex items-center gap-1">
            <div className={`h-1.5 w-1.5 rounded-full ${dataQuality.compliance === 'Healthy' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
            <span className="text-gray-400">Compliance</span>
          </span>
        </div>
      </div>
    </div>
  );
};
