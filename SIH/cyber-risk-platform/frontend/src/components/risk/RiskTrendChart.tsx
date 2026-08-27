import React from 'react';
import { Activity } from 'lucide-react';
import type { RiskTrendDataPoint } from '../../types/risk';

interface RiskTrendChartProps {
  trend: RiskTrendDataPoint[];
}

export const RiskTrendChart: React.FC<RiskTrendChartProps> = ({ trend }) => {
  if (!trend || trend.length === 0) return null;

  // Ensure trend is sorted by oldest first
  const sortedTrend = [...trend].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  
  // We want to map scores (0-100) to height (0-100%)
  const maxScore = 100;
  
  const getColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-amber-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-slate-500';
    }
  };

  return (
    <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-6 h-full flex flex-col">
      <h3 className="text-lg font-medium text-white mb-6 flex items-center gap-2">
        <Activity className="w-5 h-5 text-indigo-400" />
        Risk Trend History
      </h3>
      
      <div className="flex-1 min-h-[200px] flex items-end gap-2 relative mt-4">
        {/* Y-Axis lines */}
        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
          {[100, 75, 50, 25, 0].map((val) => (
            <div key={val} className="w-full border-t border-slate-700/30 flex items-center h-0">
              <span className="text-[10px] text-slate-500 -mt-2 -ml-6 bg-slate-900 px-1">{val}</span>
            </div>
          ))}
        </div>

        {/* Bars */}
        <div className="relative w-full h-full flex items-end justify-between px-2 z-10 gap-1">
          {sortedTrend.map((point, idx) => {
            const heightPct = (point.score / maxScore) * 100;
            const dateStr = new Date(point.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
            
            return (
              <div 
                key={idx} 
                className="group relative flex-1 max-w-[40px] flex flex-col items-center justify-end h-full"
              >
                {/* Tooltip */}
                <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-white text-xs py-1 px-2 rounded whitespace-nowrap z-20 pointer-events-none border border-slate-700">
                  {dateStr}: <span className="font-bold">{point.score.toFixed(1)}</span>
                </div>
                
                {/* Bar */}
                <div 
                  className={`w-full rounded-t-sm transition-all duration-500 ease-out ${getColor(point.risk_level)} opacity-80 group-hover:opacity-100`}
                  style={{ height: `${heightPct}%`, minHeight: '4px' }}
                />
              </div>
            );
          })}
        </div>
      </div>
      
      {/* X-Axis labels (just first and last) */}
      {sortedTrend.length > 1 && (
        <div className="flex justify-between text-xs text-slate-500 mt-4 pl-2 pr-2">
          <span>{new Date(sortedTrend[0].timestamp).toLocaleDateString()}</span>
          <span>{new Date(sortedTrend[sortedTrend.length - 1].timestamp).toLocaleDateString()}</span>
        </div>
      )}
    </div>
  );
};
