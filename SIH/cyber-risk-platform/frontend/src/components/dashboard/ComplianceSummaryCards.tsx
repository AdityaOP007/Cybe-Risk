import React from 'react';
import { ComplianceSummary } from '../../types/dashboard';
import { ShieldCheck, ShieldAlert, AlertCircle } from 'lucide-react';

interface ComplianceSummaryCardsProps {
  compliance: ComplianceSummary[];
}

export const ComplianceSummaryCards: React.FC<ComplianceSummaryCardsProps> = ({ compliance }) => {
  if (compliance.length === 0) {
    return (
      <div className="bg-[#0f172a] rounded-xl border border-gray-800 p-5 shadow-md flex items-center justify-center min-h-[200px]">
        <p className="text-gray-500 text-sm">Compliance assessment not yet completed.</p>
      </div>
    );
  }

  return (
    <div className="bg-[#0f172a] rounded-xl border border-gray-800 shadow-md flex flex-col h-full">
      <div className="p-5 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-white">Compliance Coverage</h3>
      </div>
      <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
        {compliance.map((fw) => (
          <div key={fw.framework_name} className="bg-slate-800/40 rounded-lg border border-gray-700/50 p-4">
            <div className="flex justify-between items-center mb-3">
              <h4 className="text-sm font-semibold text-white">{fw.framework_name}</h4>
              <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                fw.coverage_percentage >= 80 ? 'bg-emerald-500/20 text-emerald-400' :
                fw.coverage_percentage >= 50 ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
                {fw.coverage_percentage.toFixed(0)}%
              </span>
            </div>
            
            <div className="space-y-2 mt-4">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400 flex items-center gap-1">
                  <ShieldCheck className="h-3 w-3 text-emerald-500" /> Compliant
                </span>
                <span className="text-gray-300 font-medium">{fw.compliant}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400 flex items-center gap-1">
                  <ShieldAlert className="h-3 w-3 text-red-500" /> Non-Compliant
                </span>
                <span className="text-gray-300 font-medium">{fw.non_compliant}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400 flex items-center gap-1">
                  <AlertCircle className="h-3 w-3 text-amber-500" /> Evidence Gaps
                </span>
                <span className="text-gray-300 font-medium">{fw.insufficient_evidence}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
