import React from 'react';
import type {  BudgetSummary  } from "../../types/dashboard";
import { TrendingDown } from 'lucide-react';

interface BudgetImpactChartProps {
  budget: BudgetSummary | null;
}

export const BudgetImpactChart: React.FC<BudgetImpactChartProps> = ({ budget }) => {
  if (!budget) {
    return (
      <div className="bg-[#0f172a] rounded-xl border border-gray-800 p-5 shadow-md flex items-center justify-center min-h-[200px] h-full">
        <p className="text-gray-500 text-sm">No optimization scenario has been generated.</p>
      </div>
    );
  }

  // Calculate percentages for visual bars
  const maxRisk = 100;
  const currentRiskPct = (budget.risk_before / maxRisk) * 100;
  const targetRiskPct = (budget.risk_after / maxRisk) * 100;
  
  return (
    <div className="bg-[#0f172a] rounded-xl border border-gray-800 shadow-md flex flex-col h-full">
      <div className="p-5 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-white">Cybersecurity Investment Scenario</h3>
      </div>
      <div className="p-5 flex-1 flex flex-col justify-center">
        
        <div className="mb-6 flex justify-between items-end">
          <div>
            <p className="text-sm text-gray-400 mb-1">Scenario Budget</p>
            <p className="text-2xl font-bold text-white">₹{(budget.recommended_budget / 100000).toFixed(0)}L</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400 mb-1">Estimated Risk Reduction</p>
            <p className="text-xl font-bold text-emerald-400 flex items-center gap-1 justify-end">
              <TrendingDown className="h-5 w-5" />
              {(budget.risk_before - budget.risk_after).toFixed(1)} points
            </p>
          </div>
        </div>

        {/* Visual Bar Chart */}
        <div className="space-y-6">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-300 font-medium">Current Risk Profile</span>
              <span className="text-gray-400">{budget.risk_before.toFixed(0)}/100</span>
            </div>
            <div className="h-4 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-red-500/80 rounded-full"
                style={{ width: `${currentRiskPct}%` }}
              ></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-300 font-medium">Optimized Scenario Profile</span>
              <span className="text-emerald-400 font-medium">{budget.risk_after.toFixed(0)}/100</span>
            </div>
            <div className="h-4 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-emerald-500/80 rounded-full"
                style={{ width: `${targetRiskPct}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="mt-6 text-xs text-gray-500 text-center">
          Modeled outcome based on current assumptions and selected optimization objective.
        </div>
      </div>
    </div>
  );
};
