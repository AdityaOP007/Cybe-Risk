import React from 'react';
import { X, ShieldAlert, AlertTriangle, Network } from 'lucide-react';
import { format } from 'date-fns';
import type { ThreatIntelligenceRecord } from '../../types/threatIntelligence';

interface ThreatDetailDrawerProps {
  threat: ThreatIntelligenceRecord | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ThreatDetailDrawer: React.FC<ThreatDetailDrawerProps> = ({ threat, isOpen, onClose }) => {
  if (!isOpen || !threat) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />
      
      <div className="fixed inset-y-0 right-0 w-full max-w-2xl bg-gray-900 border-l border-gray-800 shadow-2xl z-50 flex flex-col transform transition-transform duration-300">
        <div className="flex items-center justify-between p-6 border-b border-gray-800 bg-gray-900/95 sticky top-0">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-6 h-6 text-red-500" />
              {threat.title}
            </h2>
            <div className="text-sm text-gray-400 mt-1 uppercase tracking-wider">{threat.intelligence_type} • {threat.source}</div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          
          {/* Core Info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Severity</p>
              <p className={`text-sm font-bold capitalize ${threat.severity === 'critical' ? 'text-red-500' : 'text-orange-500'}`}>
                {threat.severity}
              </p>
            </div>
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Known Exploited</p>
              {threat.known_exploited ? (
                <span className="inline-flex items-center text-red-500 text-sm font-bold">
                  <AlertTriangle className="w-4 h-4 mr-1" /> YES
                </span>
              ) : (
                <p className="text-sm text-gray-400">NO</p>
              )}
            </div>
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Confidence</p>
              <p className="text-sm font-bold text-white">{threat.confidence ? `${threat.confidence}%` : 'N/A'}</p>
            </div>
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Published</p>
              <p className="text-sm text-gray-300">
                {threat.published_at ? format(new Date(threat.published_at), 'MMM dd, yyyy') : 'N/A'}
              </p>
            </div>
          </div>

          <div className="bg-gray-800/30 p-5 rounded-xl border border-gray-700/50">
            <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
              <Info className="w-4 h-4" /> Description
            </h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              {threat.description || 'No description available for this threat record.'}
            </p>
          </div>

          {/* Indicators */}
          {threat.indicators && threat.indicators.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
                <Network className="w-4 h-4" /> Threat Indicators (IOCs)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {threat.indicators.map((ind, idx) => (
                  <div key={idx} className="bg-gray-800/50 p-3 rounded-lg flex flex-col border border-gray-700/30">
                    <span className="text-xs text-gray-500 uppercase">{ind.indicator_type}</span>
                    <span className="text-sm font-mono text-red-400 mt-1 break-all">{ind.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw Data */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-2">Raw Intelligence Data</h3>
            <div className="bg-[#0d1117] border border-gray-800 rounded-lg p-4 overflow-x-auto">
              <pre className="text-xs text-green-400 font-mono">
                {JSON.stringify(threat.raw_data, null, 2)}
              </pre>
            </div>
          </div>
          
        </div>
      </div>
    </>
  );
};

// Extracted Info component since we used it above
function Info(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M12 16v-4" />
      <path d="M12 8h.01" />
    </svg>
  );
}
