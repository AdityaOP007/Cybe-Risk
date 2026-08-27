import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { assetService } from '../services/assetService';
import { Asset, AssetPosture } from '../types/asset';
import { CriticalityBadge, EnvironmentBadge, ExposureBadge, StatusBadge } from '../components/assets/Badges';
import { Shield, Activity, Server, ArrowLeft, RefreshCw, AlertTriangle, ShieldAlert } from 'lucide-react';
import { riskService } from '../services/riskService';
import type { RiskTrendResponse } from '../types/risk';
import { RiskScoreMeter } from '../components/risk/RiskScoreMeter';
import { RiskDriversList } from '../components/risk/RiskDriversList';
import { RiskTrendChart } from '../components/risk/RiskTrendChart';

export const AssetDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [asset, setAsset] = useState<Asset | null>(null);
  const [posture, setPosture] = useState<AssetPosture | null>(null);
  const [vulnerabilities, setVulnerabilities] = useState<any[]>([]);
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [riskTrend, setRiskTrend] = useState<RiskTrendResponse | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'vulnerabilities' | 'telemetry' | 'threat-intel' | 'risk'>('overview');

  const fetchAssetData = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const [assetData, postureData, vulnsData, telemetryData, riskData] = await Promise.all([
        assetService.getAsset(id),
        assetService.getAssetPosture(id).catch(() => null), // If posture fails, don't crash whole page
        assetService.getAssetVulnerabilities(id),
        assetService.getAssetTelemetry(id),
        riskService.getAssetRiskTrend(id).catch(() => null)
      ]);
      
      setAsset(assetData);
      if (postureData) setPosture(postureData);
      setVulnerabilities(vulnsData);
      setTelemetry(telemetryData);
      if (riskData) setRiskTrend(riskData);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch asset details.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAssetData();
  }, [fetchAssetData]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex items-center gap-3 text-slate-400">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Loading asset details...</span>
        </div>
      </div>
    );
  }

  if (error || !asset) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-lg bg-red-500/10 p-4 border border-red-500/20">
          <h3 className="text-sm font-medium text-red-400">Error loading asset</h3>
          <p className="mt-2 text-sm text-red-400/80">{error || 'Asset not found'}</p>
          <div className="mt-4">
            <Link to="/assets" className="text-sm font-medium text-red-400 hover:text-red-300">
              &larr; Back to Assets
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <Link to="/assets" className="inline-flex items-center text-sm font-medium text-slate-400 hover:text-white transition-colors mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Asset Inventory
        </Link>
        <div className="md:flex md:items-start md:justify-between">
          <div className="min-w-0 flex-1">
            <h1 className="text-3xl font-bold leading-tight text-white sm:truncate sm:text-4xl">
              {asset.name}
            </h1>
            <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-1.5 capitalize">
                <Server className="h-4 w-4" />
                {asset.asset_type.replace('_', ' ')}
              </span>
              {asset.hostname && (
                <span>Host: {asset.hostname}</span>
              )}
              {asset.ip_address && (
                <span>IP: {asset.ip_address}</span>
              )}
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2 md:ml-4 md:mt-0">
            <EnvironmentBadge env={asset.environment} />
            <StatusBadge status={asset.status} />
            <ExposureBadge exposed={asset.internet_exposed} />
            <CriticalityBadge criticality={asset.criticality} />
          </div>
        </div>
      </div>

      {/* Stats/Posture Cards */}
      {posture && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
          <div className="overflow-hidden rounded-xl bg-slate-900 border border-slate-700/50 shadow">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-red-500/10 rounded-lg">
                  <ShieldAlert className="h-6 w-6 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="truncate text-sm font-medium text-slate-400">Critical Vulnerabilities</dt>
                    <dd>
                      <div className="text-2xl font-semibold text-white">{posture.critical_vulnerabilities}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          
          <div className="overflow-hidden rounded-xl bg-slate-900 border border-slate-700/50 shadow">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-orange-500/10 rounded-lg">
                  <AlertTriangle className="h-6 w-6 text-orange-400" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="truncate text-sm font-medium text-slate-400">Total Open Vulnerabilities</dt>
                    <dd>
                      <div className="text-2xl font-semibold text-white">{posture.open_vulnerabilities}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          
          <div className="overflow-hidden rounded-xl bg-slate-900 border border-slate-700/50 shadow">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-indigo-500/10 rounded-lg">
                  <Activity className="h-6 w-6 text-indigo-400" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="truncate text-sm font-medium text-slate-400">Recent Telemetry Events</dt>
                    <dd>
                      <div className="text-2xl font-semibold text-white">{posture.recent_telemetry_events}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b border-slate-700">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {[
            { id: 'overview', name: 'Overview' },
            { id: 'vulnerabilities', name: 'Vulnerabilities', count: vulnerabilities.length },
            { id: 'telemetry', name: 'Telemetry', count: telemetry.length },
            { id: 'threat-intel', name: 'Threat Intelligence' },
            { id: 'risk', name: 'Risk History' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors
                ${activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-slate-400 hover:border-slate-600 hover:text-slate-300'
                }
              `}
            >
              {tab.name}
              {tab.count !== undefined && (
                <span className={`ml-2 rounded-full py-0.5 px-2.5 text-xs font-medium ${
                  activeTab === tab.id ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-300'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-slate-900 border border-slate-700/50 rounded-xl shadow-xl overflow-hidden">
        {activeTab === 'overview' && (
          <div className="p-6">
            <h3 className="text-lg font-medium leading-6 text-white mb-4">Asset Information</h3>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2 lg:grid-cols-3">
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Description</dt>
                <dd className="mt-1 text-sm text-white">{asset.description || 'No description provided.'}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Business Value</dt>
                <dd className="mt-1 text-sm text-white">${asset.business_value.toLocaleString()}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Owner</dt>
                <dd className="mt-1 text-sm text-white">{asset.owner || 'Unassigned'}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Department</dt>
                <dd className="mt-1 text-sm text-white">{asset.department || 'Unassigned'}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Operating System</dt>
                <dd className="mt-1 text-sm text-white">{asset.operating_system || 'Unknown'}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Technology</dt>
                <dd className="mt-1 text-sm text-white">{asset.technology || 'Unknown'}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Created At</dt>
                <dd className="mt-1 text-sm text-white">{new Date(asset.created_at).toLocaleDateString()}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-slate-400">Last Updated</dt>
                <dd className="mt-1 text-sm text-white">{new Date(asset.updated_at).toLocaleDateString()}</dd>
              </div>
            </dl>
          </div>
        )}

        {activeTab === 'vulnerabilities' && (
          <div className="p-6">
            {vulnerabilities.length === 0 ? (
              <p className="text-sm text-slate-400">No vulnerabilities recorded for this asset.</p>
            ) : (
              <ul className="divide-y divide-slate-800">
                {vulnerabilities.map(v => (
                  <li key={v.id} className="py-4 flex justify-between">
                    <div>
                      <p className="text-sm font-medium text-white">{v.title}</p>
                      <p className="text-xs text-slate-500 mt-1">{v.cve_id} • Added {new Date(v.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="text-right flex flex-col items-end">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium uppercase
                        ${v.severity === 'critical' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                          v.severity === 'high' ? 'bg-orange-500/10 text-orange-400' : 'bg-yellow-500/10 text-yellow-400'}`}>
                        {v.severity}
                      </span>
                      <span className="text-xs text-slate-400 mt-1">CVSS: {v.cvss_score}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {activeTab === 'telemetry' && (
          <div className="p-6">
            {telemetry.length === 0 ? (
              <p className="text-sm text-slate-400">No telemetry events recorded for this asset.</p>
            ) : (
              <ul className="divide-y divide-slate-800">
                {telemetry.map(t => (
                  <li key={t.id} className="py-4">
                    <p className="text-sm font-medium text-white">{t.event_type} - {t.message}</p>
                    <p className="text-xs text-slate-500 mt-1">Source: {t.source} • {new Date(t.occurred_at).toLocaleString()}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {activeTab === 'threat-intel' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-white mb-4">Correlated Threat Intelligence</h3>
            <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-4 text-indigo-400">
              Integration active. See the main Threat Intelligence dashboard for a global view and detailed correlations for this asset.
            </div>
          </div>
        )}

        {activeTab === 'risk' && (
          <div className="p-6 space-y-6 bg-slate-950">
            {riskTrend ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Left Column: Meter and Summary */}
                  <div className="col-span-1 space-y-6">
                    <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center justify-center">
                      <h3 className="text-lg font-medium text-white mb-6 w-full text-left">Current Risk Score</h3>
                      <RiskScoreMeter 
                        score={riskTrend.current_score.score} 
                        level={riskTrend.current_score.risk_level} 
                        size="lg" 
                      />
                      <p className="mt-6 text-sm text-slate-400 text-center">
                        Last calculated: {new Date(riskTrend.current_score.calculated_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  {/* Right Column: Chart and Drivers */}
                  <div className="col-span-1 md:col-span-2 space-y-6">
                    <RiskDriversList score={riskTrend.current_score} />
                    <RiskTrendChart trend={riskTrend.historical_trend} />
                  </div>
                </div>
              </>
            ) : (
              <div className="p-12 text-center">
                <Shield className="mx-auto h-12 w-12 text-slate-600 mb-4" />
                <h3 className="text-lg font-medium text-white">Risk analysis not available.</h3>
                <p className="mt-2 text-sm text-slate-400">
                  Risk Engine has not calculated a score for this asset yet.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
