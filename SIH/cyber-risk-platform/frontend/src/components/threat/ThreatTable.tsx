import React from 'react';
import { format } from 'date-fns';
import { ShieldAlert, Shield, ShieldCheck, Info, AlertTriangle } from 'lucide-react';
import type { ThreatIntelligenceRecord } from '../../types/threatIntelligence';

interface ThreatTableProps {
  threats: ThreatIntelligenceRecord[];
  isLoading: boolean;
  onRowClick: (threat: ThreatIntelligenceRecord) => void;
}

const severityConfig = {
  critical: { color: 'bg-red-500/10 text-red-500 border-red-500/20', icon: ShieldAlert, label: 'CRITICAL' },
  high: { color: 'bg-orange-500/10 text-orange-500 border-orange-500/20', icon: AlertTriangle, label: 'HIGH' },
  medium: { color: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20', icon: Shield, label: 'MEDIUM' },
  low: { color: 'bg-blue-500/10 text-blue-500 border-blue-500/20', icon: ShieldCheck, label: 'LOW' },
  informational: { color: 'bg-gray-500/10 text-gray-400 border-gray-500/20', icon: Info, label: 'INFO' },
};

export const ThreatTable: React.FC<ThreatTableProps> = ({ threats, isLoading, onRowClick }) => {
  if (isLoading) {
    return (
      <div className="w-full flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (threats.length === 0) {
    return (
      <div className="w-full flex flex-col items-center justify-center py-12 text-gray-400">
        <ShieldAlert className="w-12 h-12 mb-4 text-gray-600" />
        <p>No threat intelligence found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-800 bg-gray-900/50">
      <table className="w-full text-sm text-left text-gray-300">
        <thead className="text-xs uppercase bg-gray-800/80 text-gray-400">
          <tr>
            <th className="px-4 py-3">Threat</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Severity</th>
            <th className="px-4 py-3">Source</th>
            <th className="px-4 py-3 text-center">Known Exploited</th>
            <th className="px-4 py-3">Last Seen</th>
          </tr>
        </thead>
        <tbody>
          {threats.map((threat) => {
            const config = severityConfig[threat.severity as keyof typeof severityConfig] || severityConfig.informational;
            const Icon = config.icon;
            
            return (
              <tr 
                key={threat.id} 
                onClick={() => onRowClick(threat)}
                className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors"
              >
                <td className="px-4 py-3">
                  <div className="font-medium text-white">{threat.title}</div>
                  <div className="text-xs text-gray-500 truncate max-w-xs">{threat.description}</div>
                </td>
                <td className="px-4 py-3 capitalize">{threat.intelligence_type}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${config.color}`}>
                    <Icon className="w-3 h-3 mr-1" />
                    {config.label}
                  </span>
                </td>
                <td className="px-4 py-3 uppercase tracking-wider text-xs font-semibold">{threat.source}</td>
                <td className="px-4 py-3 text-center">
                  {threat.known_exploited ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border bg-red-500/10 text-red-500 border-red-500/20">
                      YES
                    </span>
                  ) : (
                    <span className="text-gray-600">-</span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-gray-400">
                  {threat.last_seen_at ? format(new Date(threat.last_seen_at), 'MMM dd, yyyy') : 'Unknown'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
