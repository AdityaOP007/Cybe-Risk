import React, { useState, useEffect } from 'react';
import { getExecutiveDashboard, acknowledgeAlert } from '../services/dashboardService';
import { ExecutiveDashboardData } from '../types/dashboard';
import { ExecutiveHeader } from '../components/dashboard/ExecutiveHeader';
import { ExecutiveSummary } from '../components/dashboard/ExecutiveSummary';
import { TopKpiCards } from '../components/dashboard/TopKpiCards';
import { ExecutiveAlerts } from '../components/dashboard/ExecutiveAlerts';
import { TopRiskAssets } from '../components/dashboard/TopRiskAssets';
import { ActionQueue } from '../components/dashboard/ActionQueue';
import { ComplianceSummaryCards } from '../components/dashboard/ComplianceSummaryCards';
import { BudgetImpactChart } from '../components/dashboard/BudgetImpactChart';
import { Loader2 } from 'lucide-react';

export const ExecutiveDashboard: React.FC = () => {
  const [data, setData] = useState<ExecutiveDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const response = await getExecutiveDashboard();
      setData(response);
      setError(null);
    } catch (err: any) {
      console.error("Failed to load dashboard", err);
      setError("Dashboard data could not be fully loaded. Backend service may be unavailable.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await acknowledgeAlert(alertId);
      // Optimistically remove alert from UI
      if (data) {
        setData({
          ...data,
          alerts: data.alerts.filter(a => a.id !== alertId)
        });
      }
    } catch (err) {
      console.error("Failed to acknowledge alert", err);
    }
  };

  if (loading) {
    return (
      <main className="flex flex-1 flex-col items-center justify-center p-6 w-full">
        <Loader2 className="h-8 w-8 text-indigo-500 animate-spin mb-4" />
        <p className="text-gray-400">Loading Executive Command Center...</p>
      </main>
    );
  }

  if (error && !data) {
    return (
      <main className="flex flex-1 flex-col items-center justify-center p-6 w-full">
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-6 py-4 rounded-xl max-w-lg text-center">
          <p>{error}</p>
          <button 
            onClick={() => fetchDashboardData()}
            className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-300 text-sm font-medium transition-colors"
          >
            Retry
          </button>
        </div>
      </main>
    );
  }

  if (!data) return null;

  return (
    <main className="flex-1 overflow-y-auto bg-slate-950 p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header Section */}
        <ExecutiveHeader 
          organizationName="Enterprise"
          lastUpdated={data.last_updated}
          dataQuality={data.data_quality}
          onRefresh={() => fetchDashboardData(true)}
          isRefreshing={refreshing}
        />

        {/* Dynamic Executive Insights */}
        <ExecutiveSummary insights={data.insights} />

        {/* Active Alerts */}
        <ExecutiveAlerts alerts={data.alerts} onAcknowledge={handleAcknowledgeAlert} />

        {/* KPI Row */}
        <TopKpiCards 
          risk={data.risk}
          financial={data.financial}
          prediction={data.prediction}
          budget={data.budget}
          compliance={data.compliance}
        />

        {/* Multi-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          
          {/* Priority Assets (Takes up 2 columns on desktop) */}
          <div className="lg:col-span-2">
            <TopRiskAssets assets={data.top_assets} />
          </div>

          {/* Action Queue / Decisions Required (Takes up 1 column on desktop) */}
          <div className="lg:col-span-1">
            <ActionQueue recommendations={data.recommendations} budget={data.budget} />
          </div>
        </div>

        {/* Lower Row: Budget & Compliance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <BudgetImpactChart budget={data.budget} />
          <ComplianceSummaryCards compliance={data.compliance} />
        </div>

      </div>
    </main>
  );
};
