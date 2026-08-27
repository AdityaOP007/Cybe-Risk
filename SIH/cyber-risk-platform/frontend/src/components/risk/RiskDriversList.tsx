import React from 'react';
import { Shield, ShieldAlert, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { RiskScore } from '../../types/risk';

interface RiskDriversListProps {
  score: RiskScore;
}

export const RiskDriversList: React.FC<RiskDriversListProps> = ({ score }) => {
  const drivers = score.metadata_?.drivers || [];
  
  const getIconForDriver = (driver: string) => {
    const text = driver.toLowerCase();
    
    if (text.includes('critical') || text.includes('high') || text.includes('exploited')) {
      return <ShieldAlert className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />;
    }
    if (text.includes('medium') || text.includes('exposed')) {
      return <AlertTriangle className="w-5 h-5 text-orange-400 mt-0.5 flex-shrink-0" />;
    }
    if (text.includes('mitigate') || text.includes('controls')) {
      return <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />;
    }
    if (text.includes('low') || text.includes('no assets')) {
      return <Info className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />;
    }
    return <AlertCircle className="w-5 h-5 text-slate-400 mt-0.5 flex-shrink-0" />;
  };

  return (
    <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-6">
      <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
        <Shield className="w-5 h-5 text-indigo-400" />
        Key Risk Drivers
      </h3>
      
      {drivers.length === 0 ? (
        <p className="text-slate-400 text-sm italic">No risk drivers identified.</p>
      ) : (
        <ul className="space-y-4">
          {drivers.map((driver, idx) => (
            <li key={idx} className="flex items-start gap-3 bg-slate-800/30 p-3 rounded-lg border border-slate-700/30">
              {getIconForDriver(driver)}
              <span className="text-slate-300 text-sm leading-relaxed">{driver}</span>
            </li>
          ))}
        </ul>
      )}
      
      <div className="mt-6 pt-4 border-t border-slate-700/50">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">Calculation Confidence</span>
          <div className="flex items-center gap-2">
            <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${
                  (score.metadata_?.confidence || 0) > 80 ? 'bg-emerald-500' : 
                  (score.metadata_?.confidence || 0) > 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${score.metadata_?.confidence || 0}%` }}
              />
            </div>
            <span className="font-medium text-slate-300">{score.metadata_?.confidence || 0}%</span>
          </div>
        </div>
        <p className="text-xs text-slate-500 mt-2 italic">
          {score.metadata_?.explanation || 'No explanation provided.'}
        </p>
      </div>
    </div>
  );
};
