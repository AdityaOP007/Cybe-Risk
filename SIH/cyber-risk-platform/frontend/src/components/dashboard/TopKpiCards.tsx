import React from 'react';
import { 
  ShieldAlert, ShieldCheck, TrendingUp, TrendingDown, Minus, 
  DollarSign, Activity, } from 'lucide-react';
import type { 
  RiskSummary, FinancialSummary, PredictionSummary, 
  BudgetSummary, ComplianceSummary
} from '../../types/dashboard';

interface TopKpiCardsProps {
  risk: RiskSummary;
  financial: FinancialSummary | null;
  prediction: PredictionSummary | null;
  budget: BudgetSummary | null;
  compliance: ComplianceSummary[];
}

export const TopKpiCards: React.FC<TopKpiCardsProps> = ({
  risk, financial, prediction, compliance
}) => {
  const formatCurrency = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(1)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)} Lakh`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const TrendIcon = ({ trend }: { trend: string }) => {
    if (trend === 'increasing') return <TrendingUp className="h-4 w-4 text-red-500" />;
    if (trend === 'decreasing') return <TrendingDown className="h-4 w-4 text-emerald-500" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  // Determine overall compliance coverage
  const totalCoverage = compliance.length > 0 
    ? compliance.reduce((acc, curr) => acc + curr.coverage_percentage, 0) / compliance.length 
    : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      
      {/* 1. Overall Risk */}
      <div className="bg-[#0f172a] rounded-xl p-5 border border-gray-800 shadow-md">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Overall Cyber Risk</h3>
          <div className="p-2 bg-indigo-500/10 rounded-lg">
            <ShieldAlert className="h-4 w-4 text-indigo-400" />
          </div>
        </div>
        <div className="flex items-end gap-3">
          <span className="text-3xl font-bold text-white">{risk.current_score.toFixed(0)}</span>
          <span className="text-sm text-gray-500 mb-1">/ 100</span>
        </div>
        <div className="mt-3 flex items-center justify-between text-xs">
          <span className={`font-medium px-2 py-0.5 rounded ${
            risk.risk_level === 'Critical' ? 'bg-red-500/20 text-red-400' :
            risk.risk_level === 'High' ? 'bg-orange-500/20 text-orange-400' :
            risk.risk_level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-emerald-500/20 text-emerald-400'
          }`}>
            {risk.risk_level}
          </span>
          <div className="flex items-center gap-1 text-gray-400">
            <TrendIcon trend={risk.trend} />
            <span>
              {risk.change ? `${risk.change > 0 ? '+' : ''}${risk.change.toFixed(1)} from prev` : 'Trend unavailable'}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Financial Exposure */}
      <div className="bg-[#0f172a] rounded-xl p-5 border border-gray-800 shadow-md">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Modeled Financial Exposure</h3>
          <div className="p-2 bg-rose-500/10 rounded-lg">
            <DollarSign className="h-4 w-4 text-rose-400" />
          </div>
        </div>
        <div className="flex items-end gap-2">
          {financial ? (
            <span className="text-3xl font-bold text-white">{formatCurrency(financial.modeled_exposure)}</span>
          ) : (
            <span className="text-xl font-medium text-gray-500">Unavailable</span>
          )}
        </div>
        <div className="mt-3 flex items-center text-xs text-gray-400">
          <span>Expected Annual Loss: {financial ? formatCurrency(financial.expected_annual_loss) : '-'}</span>
        </div>
      </div>

      {/* 3. Predicted Risk */}
      <div className="bg-[#0f172a] rounded-xl p-5 border border-gray-800 shadow-md">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">30-Day Risk Forecast</h3>
          <div className="p-2 bg-blue-500/10 rounded-lg">
            <Activity className="h-4 w-4 text-blue-400" />
          </div>
        </div>
        <div className="flex items-end gap-3">
          {prediction ? (
            <>
              <span className="text-3xl font-bold text-white">{prediction.forecast_30_day.toFixed(0)}</span>
              <span className="text-sm text-gray-500 mb-1">/ 100</span>
            </>
          ) : (
            <span className="text-xl font-medium text-gray-500">Model Pending</span>
          )}
        </div>
        <div className="mt-3 flex items-center text-xs text-gray-400 gap-1">
          {prediction && (
            <>
              <TrendIcon trend={prediction.trend} />
              <span>Projected to be {prediction.trend}</span>
            </>
          )}
        </div>
      </div>

      {/* 4. Compliance Coverage */}
      <div className="bg-[#0f172a] rounded-xl p-5 border border-gray-800 shadow-md">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Avg Compliance Coverage</h3>
          <div className="p-2 bg-emerald-500/10 rounded-lg">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          </div>
        </div>
        <div className="flex items-end gap-1">
          <span className="text-3xl font-bold text-white">{totalCoverage.toFixed(0)}%</span>
        </div>
        <div className="mt-3 flex items-center text-xs text-gray-400">
          <span>Across {compliance.length} tracked frameworks</span>
        </div>
      </div>

    </div>
  );
};
