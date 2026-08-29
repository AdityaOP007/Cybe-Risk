import React from 'react';
import type {  RecommendationSummary, BudgetSummary  } from "../../types/dashboard";
import { CheckCircle, AlertTriangle, ArrowRight, Shield } from 'lucide-react';

interface ActionQueueProps {
  recommendations: RecommendationSummary[];
  budget: BudgetSummary | null;
}

export const ActionQueue: React.FC<ActionQueueProps> = ({ recommendations, budget }) => {
  return (
    <div className="bg-[#0f172a] rounded-xl border border-gray-800 shadow-md flex flex-col h-full">
      <div className="p-5 border-b border-gray-800 flex justify-between items-center">
        <h3 className="text-lg font-semibold text-white">Executive Decisions Required</h3>
        <span className="text-xs bg-indigo-500/20 text-indigo-400 px-2 py-1 rounded">
          {recommendations.length} Pending
        </span>
      </div>
      <div className="p-5 flex-1 overflow-y-auto">
        <div className="space-y-4">
          
          {/* Budget Decision if available */}
          {budget && (
            <div className="bg-slate-800/50 rounded-lg p-4 border border-indigo-500/30">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-indigo-400" />
                  <h4 className="text-sm font-semibold text-white">Approve Cybersecurity Portfolio</h4>
                </div>
                <span className="text-xs text-indigo-400 font-medium">Strategic</span>
              </div>
              <p className="text-sm text-gray-400 mb-3">
                Review ₹{(budget.budget_used / 100000).toFixed(1)}L scenario to reduce risk by {(budget.risk_before - budget.risk_after).toFixed(0)} points.
              </p>
              <button className="flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300">
                Review Scenario <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          )}

          {/* Top Recommendations */}
          {recommendations.slice(0, 4).map((rec) => (
            <div key={rec.recommendation_id} className="bg-slate-800/30 rounded-lg p-4 border border-gray-700/50">
              <div className="flex items-start justify-between mb-2">
                <div className="flex flex-col gap-1">
                  <h4 className="text-sm font-semibold text-white">{rec.action}</h4>
                  <span className="text-xs text-gray-400">{rec.asset_name || 'Organization Wide'}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  rec.priority === 'Critical' ? 'bg-red-500/20 text-red-400' :
                  rec.priority === 'High' ? 'bg-orange-500/20 text-orange-400' :
                  'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {rec.priority}
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-3 flex items-center gap-2">
                <AlertTriangle className="h-3 w-3 text-amber-500" />
                Reduces modeled risk by {rec.estimated_risk_reduction.toFixed(1)} points
              </p>
              <button className="flex items-center gap-1 text-xs font-medium text-gray-300 hover:text-white">
                View Details <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          ))}

          {recommendations.length === 0 && !budget && (
            <div className="text-center py-8">
              <CheckCircle className="h-8 w-8 text-emerald-500 mx-auto mb-3" />
              <p className="text-sm text-gray-400">No urgent decisions required at this time.</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
