import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/common/Header';
import { useBackendStatus } from './hooks/useBackendStatus';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Assets } from './pages/Assets';
import { AssetDetails } from './pages/AssetDetails';
import { Telemetry } from './pages/Telemetry';
import { ThreatIntelligence } from './pages/ThreatIntelligence';
import { FinancialRisk } from './pages/FinancialRisk';

import React, { useState, useEffect } from 'react';
import { riskService } from './services/riskService';
import api from './services/api';
import type { RiskTrendResponse } from './types/risk';
import { RiskScoreMeter } from './components/risk/RiskScoreMeter';
import { Activity } from 'lucide-react';

function Dashboard() {
  const backendStatus = useBackendStatus();
  const [orgRisk, setOrgRisk] = useState<RiskTrendResponse | null>(null);

  useEffect(() => {
    const fetchOrgRisk = async () => {
      try {
        const response = await api.get<{ items: { id: string }[] }>('/api/v1/organizations/');
        if (response.items && response.items.length > 0) {
          const orgId = response.items[0].id;
          const risk = await riskService.getOrganizationRiskTrend(orgId);
          setOrgRisk(risk);
        }
      } catch (err) {
        console.error('Failed to fetch organizational risk', err);
      }
    };
    if (backendStatus === 'connected') {
      fetchOrgRisk();
    }
  }, [backendStatus]);

  return (
    <main className="flex flex-1 flex-col items-center justify-start px-6 mt-12 w-full max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-2xl shadow-indigo-500/30">
          <Activity className="h-10 w-10 text-white" />
        </div>
        <h2 className="mb-3 text-4xl font-bold tracking-tight text-white">
          Cyber Risk Platform
        </h2>
        <p className="mx-auto max-w-lg text-lg text-slate-400">
          AI-powered cyber risk quantification and decision intelligence
          for modern enterprises.
        </p>
      </div>

      <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl">
        {/* Status Card */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6 shadow-xl backdrop-blur-sm">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
            System Status
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-lg bg-slate-800/50 px-4 py-3">
              <span className="text-sm text-slate-300">Frontend</span>
              <div className="flex items-center gap-2">
                <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" />
                <span className="text-sm font-medium text-emerald-400">Running</span>
              </div>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-800/50 px-4 py-3">
              <span className="text-sm text-slate-300">Backend API</span>
              <div className="flex items-center gap-2">
                <span
                  className={`inline-block h-2 w-2 rounded-full ${
                    backendStatus === 'connected'
                      ? 'bg-emerald-400'
                      : backendStatus === 'checking'
                        ? 'bg-amber-400 animate-pulse'
                        : 'bg-red-400'
                  }`}
                />
                <span
                  className={`text-sm font-medium ${
                    backendStatus === 'connected'
                      ? 'text-emerald-400'
                      : backendStatus === 'checking'
                        ? 'text-amber-400'
                        : 'text-red-400'
                  }`}
                >
                  {backendStatus === 'connected'
                    ? 'Connected'
                    : backendStatus === 'checking'
                      ? 'Checking...'
                      : 'Unavailable'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Organization Risk Card */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6 shadow-xl backdrop-blur-sm flex flex-col items-center justify-center">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400 w-full text-left">
            Organizational Risk Profile
          </h3>
          {orgRisk ? (
            <div className="flex flex-col items-center">
              <RiskScoreMeter 
                score={orgRisk.current_score.score} 
                level={orgRisk.current_score.risk_level} 
                size="md" 
              />
              <p className="mt-4 text-sm text-slate-300 text-center">
                {orgRisk.current_score.metadata_.explanation}
              </p>
            </div>
          ) : (
            <div className="text-slate-500 text-sm flex flex-col items-center">
              <span>Waiting for calculation...</span>
            </div>
          )}
        </div>
      </div>
      
      <p className="mt-12 text-xs text-slate-500">
        Module 06 — Cyber Risk Engine & Risk Quantification
      </p>
    </main>
  );
}

function App() {
  const backendStatus = useBackendStatus();

  return (
    <Router>
      <div className="flex min-h-screen flex-col bg-slate-950">
        <Header backendStatus={backendStatus} />
        
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/assets" element={<Assets />} />
          <Route path="/assets/:id" element={<AssetDetails />} />
          <Route path="/telemetry" element={<Telemetry />} />
          <Route path="/threat-intel" element={<ThreatIntelligence />} />
          <Route path="/financial-risk" element={<FinancialRisk />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
