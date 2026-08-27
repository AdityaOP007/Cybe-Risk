import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  TrendingDown, 
  Clock, 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  IndianRupee,
  ChevronRight,
  Settings,
  RefreshCw
} from 'lucide-react';
import { recommendationService } from '../services/recommendationService';
import type { Recommendation } from '../types/recommendation';

export function Recommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const data = await recommendationService.getRecommendations();
      setRecommendations(data);
      if (data.length > 0) setSelectedRec(data[0]);
    } catch (err) {
      setError('Failed to fetch recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      const data = await recommendationService.generateRecommendations();
      setRecommendations(data);
      if (data.length > 0) setSelectedRec(data[0]);
    } catch (err) {
      setError('Failed to generate recommendations.');
    } finally {
      setGenerating(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'text-red-400 border-red-400/30 bg-red-400/10';
      case 'high': return 'text-orange-400 border-orange-400/30 bg-orange-400/10';
      case 'medium': return 'text-amber-400 border-amber-400/30 bg-amber-400/10';
      case 'low': return 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10';
      default: return 'text-slate-400 border-slate-400/30 bg-slate-400/10';
    }
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return '₹0.00';
    return `₹${(amount / 10000000).toFixed(2)} Cr`;
  };

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Activity className="h-8 w-8 animate-pulse text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="h-6 w-6 text-indigo-400" />
            AI Mitigation Recommendations
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Prioritized actions derived from threat intelligence, telemetry, and financial exposure analysis.
          </p>
        </div>
        
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${generating ? 'animate-spin' : ''}`} />
          {generating ? 'Scanning Infrastructure...' : 'Run Analysis Pipeline'}
        </button>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* List View */}
        <div className="lg:col-span-1 flex flex-col gap-3">
          {recommendations.length === 0 ? (
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-8 text-center text-slate-400">
              No active recommendations found.
            </div>
          ) : (
            recommendations.map(rec => (
              <button
                key={rec.id}
                onClick={() => setSelectedRec(rec)}
                className={`text-left rounded-xl border p-4 transition-all ${
                  selectedRec?.id === rec.id
                  ? 'border-indigo-500 bg-indigo-500/10'
                  : 'border-slate-700/50 bg-slate-900/60 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${getPriorityColor(rec.priority)} uppercase tracking-wider`}>
                    {rec.priority}
                  </span>
                  {rec.metadata?.expected_financial_benefit ? (
                    <span className="text-xs font-medium text-emerald-400 flex items-center">
                      <TrendingDown className="h-3 w-3 mr-1" />
                      {formatCurrency(rec.metadata.expected_financial_benefit)}
                    </span>
                  ) : null}
                </div>
                <h3 className="text-sm font-medium text-white line-clamp-2">{rec.title}</h3>
                <div className="mt-3 flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {rec.metadata?.urgency || 'Standard'}
                  </span>
                  <span className="flex items-center gap-1">
                    <Settings className="h-3 w-3" />
                    {rec.metadata?.implementation_effort || 'Unknown'} Effort
                  </span>
                </div>
              </button>
            ))
          )}
        </div>

        {/* Detailed View */}
        <div className="lg:col-span-2">
          {selectedRec ? (
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 overflow-hidden h-full">
              {/* Header */}
              <div className="border-b border-slate-800 p-6 bg-slate-800/20">
                <div className="flex items-center gap-3 mb-4">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${getPriorityColor(selectedRec.priority)} uppercase tracking-wider`}>
                    {selectedRec.priority} Priority
                  </span>
                  <span className="text-xs font-medium px-2 py-0.5 rounded border border-indigo-500/30 bg-indigo-500/10 text-indigo-300">
                    Confidence: {selectedRec.metadata?.confidence.toFixed(0)}%
                  </span>
                </div>
                <h2 className="text-xl font-bold text-white mb-2">{selectedRec.title}</h2>
                <p className="text-sm text-slate-400">{selectedRec.description}</p>
              </div>

              <div className="p-6 space-y-8">
                
                {/* Expected Outcomes */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4">
                    <div className="flex items-center gap-2 mb-2 text-emerald-400">
                      <TrendingDown className="h-5 w-5" />
                      <h4 className="text-sm font-semibold">Risk Reduction</h4>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      -{selectedRec.expected_risk_reduction?.toFixed(1) || 0} pts
                    </p>
                    <p className="text-xs text-slate-400 mt-1">Target Risk Driver: <span className="text-slate-300">{selectedRec.metadata?.risk_driver}</span></p>
                  </div>

                  <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-4">
                    <div className="flex items-center gap-2 mb-2 text-indigo-400">
                      <IndianRupee className="h-5 w-5" />
                      <h4 className="text-sm font-semibold">Financial Benefit</h4>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      {formatCurrency(selectedRec.metadata?.expected_financial_benefit)}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">Reduction in Expected Annual Loss</p>
                  </div>
                </div>

                {/* Rationale & Execution */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <Activity className="h-4 w-4 text-indigo-400" />
                      AI Rationale
                    </h4>
                    <p className="text-sm text-slate-300 leading-relaxed bg-slate-800/50 p-4 rounded-lg">
                      {selectedRec.metadata?.rationale}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <Settings className="h-4 w-4 text-indigo-400" />
                      Execution Profile
                    </h4>
                    <ul className="space-y-3 bg-slate-800/50 p-4 rounded-lg">
                      <li className="flex justify-between text-sm">
                        <span className="text-slate-400">Urgency</span>
                        <span className="font-medium text-white">{selectedRec.metadata?.urgency}</span>
                      </li>
                      <li className="flex justify-between text-sm">
                        <span className="text-slate-400">Effort Required</span>
                        <span className="font-medium text-white">{selectedRec.metadata?.implementation_effort}</span>
                      </li>
                      <li className="flex justify-between text-sm">
                        <span className="text-slate-400">Estimated Cost</span>
                        <span className="font-medium text-white">₹{selectedRec.estimated_cost?.toLocaleString()}</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Evidence */}
                {selectedRec.metadata?.evidence && selectedRec.metadata.evidence.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-amber-400" />
                      Correlated Evidence
                    </h4>
                    <div className="space-y-3">
                      {selectedRec.metadata.evidence.map((ev, idx) => (
                        <div key={idx} className="flex items-start gap-3 rounded-lg border border-slate-700/50 bg-slate-800/30 p-3">
                          <ChevronRight className="h-5 w-5 text-slate-500 mt-0.5 shrink-0" />
                          <div>
                            <span className="text-xs font-semibold text-indigo-300 uppercase tracking-wider">{ev.source}</span>
                            <p className="text-sm text-slate-300 mt-1">{ev.detail}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Actions */}
                <div className="pt-4 border-t border-slate-800 flex justify-end gap-3">
                  <button className="px-4 py-2 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-800 text-sm font-medium transition-colors">
                    Reject
                  </button>
                  <button className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 text-sm font-medium flex items-center gap-2 transition-colors">
                    <CheckCircle2 className="h-4 w-4" />
                    Accept Mitigation
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex h-full items-center justify-center rounded-xl border border-slate-700/50 bg-slate-900/60">
              <p className="text-slate-400">Select a recommendation to view details.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
