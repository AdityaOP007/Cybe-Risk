import { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingDown, 
  Target, 
  ShieldCheck, 
  CheckCircle2, 
  Settings2, 
  Activity,
  IndianRupee,
  PieChart
} from 'lucide-react';
import { optimizationService } from '../services/optimizationService';
import type { OptimizationRunRequest, OptimizationRun, CybersecurityInvestment } from '../types/optimization';

export function BudgetOptimization() {
  const [budget, setBudget] = useState<number>(2500000);
  const [objective, setObjective] = useState<string>('balanced');
  const [loading, setLoading] = useState(false);
  const [optimizationRun, setOptimizationRun] = useState<OptimizationRun | null>(null);
  const [investments, setInvestments] = useState<CybersecurityInvestment[]>([]);

  useEffect(() => {
    fetchInvestments();
    // Fetch initial default run
    handleOptimize(2500000, 'balanced');
  }, []);

  const fetchInvestments = async () => {
    try {
      const data = await optimizationService.getInvestments();
      setInvestments(data);
    } catch (error) {
      console.error('Failed to fetch investments', error);
    }
  };

  const handleOptimize = async (customBudget?: number, customObjective?: string) => {
    setLoading(true);
    try {
      const req: OptimizationRunRequest = {
        budget: customBudget ?? budget,
        currency: 'INR',
        horizon_months: 12,
        objective: customObjective ?? objective,
        weights: {
          risk_weight: 0.4,
          financial_weight: 0.3,
          criticality_weight: 0.15,
          urgency_weight: 0.10,
          confidence_weight: 0.05
        }
      };
      const run = await optimizationService.runOptimization(req);
      setOptimizationRun(run);
    } catch (error) {
      console.error('Optimization failed', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount?: number) => {
    if (amount === undefined || amount === null) return '₹0.00';
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)} Lakh`;
    return `₹${amount.toLocaleString()}`;
  };

  const getSelectedInvestments = () => {
    if (!optimizationRun || optimizationRun.portfolios.length === 0) return [];
    const selectedIds = optimizationRun.portfolios[0].selected_investments;
    return investments.filter(i => selectedIds.includes(i.id));
  };

  const getRejectedInvestments = () => {
    if (!optimizationRun || optimizationRun.portfolios.length === 0) return [];
    const selectedIds = optimizationRun.portfolios[0].selected_investments;
    return investments.filter(i => !selectedIds.includes(i.id));
  };

  const selectedInvestments = getSelectedInvestments();
  const rejectedInvestments = getRejectedInvestments();

  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Target className="h-6 w-6 text-indigo-400" />
          Cybersecurity Investment Command Center
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Optimize capital allocation against cyber risk using deterministic knapsack selection.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        
        {/* Controls Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
              <Settings2 className="h-4 w-4 text-indigo-400" />
              Optimization Parameters
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Available Budget (INR)</label>
                <select 
                  value={budget}
                  onChange={(e) => {
                    setBudget(Number(e.target.value));
                    handleOptimize(Number(e.target.value), objective);
                  }}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 p-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value={1000000}>₹10 Lakh</option>
                  <option value={2500000}>₹25 Lakh</option>
                  <option value={5000000}>₹50 Lakh</option>
                  <option value={10000000}>₹1 Crore</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Objective</label>
                <select 
                  value={objective}
                  onChange={(e) => {
                    setObjective(e.target.value);
                    handleOptimize(budget, e.target.value);
                  }}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 p-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="balanced">Balanced (Risk + Financial)</option>
                  <option value="risk_first">Maximize Risk Reduction</option>
                  <option value="financial_first">Maximize Financial Reduction</option>
                </select>
              </div>

              <div className="pt-4 border-t border-slate-800">
                <button
                  onClick={() => handleOptimize()}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {loading ? <Activity className="h-4 w-4 animate-spin" /> : <BarChart3 className="h-4 w-4" />}
                  Run Optimizer
                </button>
              </div>
            </div>
          </div>
          
          {optimizationRun && (
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
                <PieChart className="h-4 w-4 text-emerald-400" />
                Budget Utilization
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Total Budget:</span>
                  <span className="text-white font-medium">{formatCurrency(optimizationRun.budget)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Total Cost:</span>
                  <span className="text-emerald-400 font-medium">{formatCurrency(optimizationRun.total_cost)}</span>
                </div>
                <div className="flex justify-between text-sm pt-2 border-t border-slate-800">
                  <span className="text-slate-400">Remaining:</span>
                  <span className="text-white font-medium">{formatCurrency(optimizationRun.remaining_budget)}</span>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-2 h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div 
                    className="h-full bg-emerald-500 rounded-full" 
                    style={{ width: `${(optimizationRun.total_cost / optimizationRun.budget) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Area */}
        <div className="lg:col-span-3 space-y-6">
          
          {loading && !optimizationRun ? (
            <div className="flex h-64 items-center justify-center rounded-xl border border-slate-700/50 bg-slate-900/60">
              <Activity className="h-8 w-8 animate-pulse text-indigo-500" />
            </div>
          ) : optimizationRun ? (
            <>
              {/* Top KPIs */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-6 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                    <TrendingDown className="h-16 w-16 text-emerald-400" />
                  </div>
                  <h3 className="text-sm font-medium text-emerald-400 mb-1">Modeled Risk Reduction</h3>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white">-{optimizationRun.risk_reduction?.toFixed(1)}</span>
                    <span className="text-sm text-slate-400">pts</span>
                  </div>
                  <div className="mt-2 text-xs text-slate-400">
                    From {optimizationRun.risk_before?.toFixed(1)} to {optimizationRun.risk_after?.toFixed(1)}
                  </div>
                </div>

                <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-6 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                    <IndianRupee className="h-16 w-16 text-indigo-400" />
                  </div>
                  <h3 className="text-sm font-medium text-indigo-400 mb-1">Modeled Financial Reduction</h3>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white">{formatCurrency(optimizationRun.financial_reduction)}</span>
                  </div>
                  <div className="mt-2 text-xs text-slate-400">
                    From {formatCurrency(optimizationRun.financial_before)} to {formatCurrency(optimizationRun.financial_after)}
                  </div>
                </div>
              </div>

              {/* Engine Explanation */}
              <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
                <div className="flex items-start gap-3">
                  <ShieldCheck className="h-5 w-5 text-indigo-400 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-1">Optimization Rationale</h4>
                    <p className="text-sm text-slate-300 leading-relaxed">
                      {optimizationRun.portfolios[0]?.metadata?.explanation || 'Optimal portfolio selected.'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Selected Portfolio */}
              <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 overflow-hidden">
                <div className="border-b border-slate-800 p-5 bg-slate-800/20 flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-white">Optimized Investment Portfolio</h3>
                  <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {selectedInvestments.length} Selected
                  </span>
                </div>
                
                <div className="divide-y divide-slate-800/50">
                  {selectedInvestments.map(inv => (
                    <div key={inv.id} className="p-5 hover:bg-slate-800/30 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          <h4 className="text-sm font-medium text-white">{inv.title}</h4>
                        </div>
                        <span className="text-sm font-semibold text-indigo-400">{formatCurrency(inv.cost)}</span>
                      </div>
                      <p className="text-sm text-slate-400 mb-3 pl-6 line-clamp-2">{inv.description}</p>
                      
                      <div className="flex items-center gap-4 pl-6">
                        <div className="flex items-center gap-1.5 text-xs">
                          <TrendingDown className="h-3.5 w-3.5 text-emerald-400" />
                          <span className="text-slate-300">-{inv.risk_reduction?.toFixed(1)} Risk</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs">
                          <IndianRupee className="h-3.5 w-3.5 text-indigo-400" />
                          <span className="text-slate-300">{formatCurrency(inv.financial_reduction)} Avoidance</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs">
                          <Activity className="h-3.5 w-3.5 text-slate-400" />
                          <span className="text-slate-400">{inv.confidence}% Confidence</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {selectedInvestments.length === 0 && (
                    <div className="p-8 text-center text-slate-400">
                      No investments could be selected within the current budget constraints.
                    </div>
                  )}
                </div>
              </div>
              
              {/* Rejected / Not Selected */}
              {rejectedInvestments.length > 0 && (
                <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 overflow-hidden opacity-75">
                  <div className="border-b border-slate-800 p-4 bg-slate-800/20">
                    <h3 className="text-sm font-medium text-slate-300">Not Selected (Insufficient Budget or Lower Marginal Benefit)</h3>
                  </div>
                  <div className="divide-y divide-slate-800/50">
                    {rejectedInvestments.map(inv => (
                      <div key={inv.id} className="p-4 flex justify-between items-center bg-slate-800/10">
                        <span className="text-sm text-slate-400">{inv.title}</span>
                        <span className="text-xs text-slate-500">{formatCurrency(inv.cost)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
