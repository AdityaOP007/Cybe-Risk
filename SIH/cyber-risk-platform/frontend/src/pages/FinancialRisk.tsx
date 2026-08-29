import { useEffect, useState } from 'react';
import { DollarSign, RefreshCw, AlertTriangle, Shield, Activity, BarChart3, TrendingUp } from 'lucide-react';
import type { OrganizationFinancialRiskSummary } from '../types/financialRisk';
import financialRiskService from '../services/financialRiskService';
import api from "../services/api";

const formatCurrency = (value: number, currency: string = 'INR') => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0,
  }).format(value);
};

const FinancialRisk = () => {
  const [user, setUser] = useState<{organization_id: string} | null>(null);
  useEffect(() => {
    api.get<any[]>('/api/v1/organizations/').then(orgs => {
      if (orgs && orgs.length > 0) setUser({ organization_id: orgs[0].id });
    });
  }, []);
  const [summary, setSummary] = useState<OrganizationFinancialRiskSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRecalculating, setIsRecalculating] = useState(false);

  const fetchFinancialRisk = async () => {
    if (!user?.organization_id) return;
    setLoading(true);
    try {
      const data = await financialRiskService.getOrganizationFinancialRisk(user.organization_id);
      setSummary(data);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setSummary(null);
      } else {
        setError('Failed to load financial risk data.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    if (!user?.organization_id) return;
    setIsRecalculating(true);
    try {
      await financialRiskService.calculateOrganizationFinancialRisk(user.organization_id);
      await fetchFinancialRisk();
    } catch (err) {
      setError('Failed to recalculate financial risk.');
    } finally {
      setIsRecalculating(false);
    }
  };

  useEffect(() => {
    fetchFinancialRisk();
  }, [user?.organization_id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-center gap-3">
        <AlertTriangle className="w-5 h-5" />
        <p>{error}</p>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <DollarSign className="w-6 h-6 text-rose-500" />
          Financial Risk Quantification
        </h1>
        <div className="bg-blue-500/10 border border-blue-500/20 p-6 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3 text-blue-400">
            <AlertTriangle className="w-5 h-5" />
            <p>No financial risk data found for your organization. You may need to run the Risk Engine first.</p>
          </div>
          <button 
            onClick={handleRecalculate}
            disabled={isRecalculating}
            className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 rounded-lg transition-colors flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${isRecalculating ? 'animate-spin' : ''}`} />
            Recalculate Now
          </button>
        </div>
      </div>
    );
  }

  const { aggregate_breakdown } = summary;

  const breakdownItems = [
    { label: 'Data Loss', value: aggregate_breakdown.data_loss, color: 'bg-rose-500' },
    { label: 'Business Interruption', value: aggregate_breakdown.business_interruption_loss, color: 'bg-orange-500' },
    { label: 'Regulatory/Legal', value: aggregate_breakdown.regulatory_legal_exposure, color: 'bg-purple-500' },
    { label: 'Recovery', value: aggregate_breakdown.recovery_loss, color: 'bg-blue-500' },
    { label: 'Direct Cost', value: aggregate_breakdown.direct_loss, color: 'bg-cyan-500' },
    { label: 'Customer Impact', value: aggregate_breakdown.customer_impact, color: 'bg-pink-500' },
    { label: 'Third-Party', value: aggregate_breakdown.third_party_impact, color: 'bg-amber-500' },
    { label: 'Fraud', value: aggregate_breakdown.fraud_loss, color: 'bg-indigo-500' },
    { label: 'Reputation', value: aggregate_breakdown.reputation_revenue_impact, color: 'bg-emerald-500' },
  ].filter(item => item.value > 0).sort((a, b) => b.value - a.value);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <DollarSign className="w-6 h-6 text-rose-500" />
            Financial Risk Quantification
          </h1>
          <p className="text-gray-400 text-sm mt-1">FAIR-inspired financial exposure modeling</p>
        </div>
        <button 
          onClick={handleRecalculate}
          disabled={isRecalculating}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRecalculating ? 'animate-spin text-rose-400' : ''}`} />
          {isRecalculating ? 'Recalculating...' : 'Recalculate'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Modeled Potential Loss */}
        <div className="bg-[#0f172a] rounded-xl p-6 border border-gray-800 shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Modeled Potential Loss</h3>
            <div className="p-2 bg-orange-500/10 rounded-lg">
              <TrendingUp className="h-5 w-5 text-orange-400" />
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {formatCurrency(summary.total_potential_loss, summary.currency)}
          </div>
          <p className="text-sm text-gray-500">Total exposure across all identified risk scenarios</p>
        </div>

        {/* Expected Annual Loss */}
        <div className="bg-[#0f172a] rounded-xl p-6 border border-gray-800 shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Expected Annual Loss (EAL)</h3>
            <div className="p-2 bg-rose-500/10 rounded-lg">
              <BarChart3 className="h-5 w-5 text-rose-400" />
            </div>
          </div>
          <div className="text-3xl font-bold text-rose-400 mb-2">
            {formatCurrency(summary.total_expected_annual_loss, summary.currency)}
          </div>
          <p className="text-sm text-gray-500">Probability-weighted annualized financial exposure</p>
        </div>

        {/* Model Confidence */}
        <div className="bg-[#0f172a] rounded-xl p-6 border border-gray-800 shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Model Confidence</h3>
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <Shield className="h-5 w-5 text-emerald-400" />
            </div>
          </div>
          <div className="flex items-end gap-3 mb-2">
            <div className="text-3xl font-bold text-white">
              {summary.average_confidence.toFixed(0)}%
            </div>
            <div className={`px-2 py-0.5 rounded text-xs font-medium mb-1 ${
              summary.average_confidence >= 80 ? 'bg-emerald-500/20 text-emerald-400' : 
              summary.average_confidence >= 50 ? 'bg-orange-500/20 text-orange-400' : 
              'bg-red-500/20 text-red-400'
            }`}>
              {summary.average_confidence >= 80 ? 'High' : summary.average_confidence >= 50 ? 'Medium' : 'Low'}
            </div>
          </div>
          <p className="text-sm text-gray-500">Based on completeness of data and assumptions</p>
        </div>
      </div>

      {/* Breakdown */}
      <div className="bg-[#0f172a] rounded-xl p-6 border border-gray-800 shadow-md">
        <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          Potential Loss Breakdown
        </h3>
        <div className="space-y-4">
          {breakdownItems.map((item, idx) => {
            const percentage = (item.value / summary.total_potential_loss) * 100;
            return (
              <div key={idx}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-300">{item.label}</span>
                  <span className="text-sm font-bold text-white">
                    {formatCurrency(item.value, summary.currency)} 
                    <span className="text-gray-500 font-normal ml-2">({percentage.toFixed(1)}%)</span>
                  </span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div className={`${item.color} h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Assets */}
      <div className="bg-[#0f172a] rounded-xl border border-gray-800 shadow-md overflow-hidden">
        <div className="p-6 border-b border-gray-800">
          <h3 className="text-lg font-semibold text-white">Top Financial Risk Assets</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="text-xs uppercase bg-gray-900/50 text-gray-500 border-b border-gray-800">
              <tr>
                <th className="px-6 py-4 font-medium">Asset ID</th>
                <th className="px-6 py-4 font-medium text-right">Cyber Risk Factor</th>
                <th className="px-6 py-4 font-medium text-right">Event Frequency</th>
                <th className="px-6 py-4 font-medium text-right">Potential Loss</th>
                <th className="px-6 py-4 font-medium text-right">Expected Annual Loss</th>
                <th className="px-6 py-4 font-medium text-right">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {summary.top_financial_risk_assets.map((asset) => (
                <tr key={asset.id} className="hover:bg-gray-800/30 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">{asset.asset_id.substring(0, 8)}...</td>
                  <td className="px-6 py-4 text-right">
                    <span className="px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs">
                      {asset.metadata?.factors?.likelihood || "N/A"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">{asset.metadata?.annual_event_frequency || 0} / yr</td>
                  <td className="px-6 py-4 text-right text-orange-400 font-medium">
                    {formatCurrency(asset.potential_loss, asset.currency)}
                  </td>
                  <td className="px-6 py-4 text-right text-rose-500 font-bold">
                    {formatCurrency(asset.expected_loss, asset.currency)}
                  </td>
                  <td className="px-6 py-4 text-right text-gray-300">{asset.confidence}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FinancialRisk;
