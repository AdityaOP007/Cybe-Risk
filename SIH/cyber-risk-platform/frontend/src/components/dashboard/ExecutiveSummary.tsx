import React from 'react';
import { ExecutiveInsight } from '../../types/dashboard';
import { Lightbulb } from 'lucide-react';

interface ExecutiveSummaryProps {
  insights: ExecutiveInsight[];
}

export const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({ insights }) => {
  if (insights.length === 0) return null;
  
  return (
    <div className="bg-indigo-500/10 rounded-xl border border-indigo-500/20 p-5 mb-8">
      <div className="flex items-start gap-4">
        <div className="mt-1 flex-shrink-0">
          <Lightbulb className="h-5 w-5 text-indigo-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-indigo-300 uppercase tracking-wider mb-2">Executive Summary</h3>
          <p className="text-sm text-gray-300 leading-relaxed">
            {insights.map(i => i.content).join(' ')}
          </p>
        </div>
      </div>
    </div>
  );
};
