import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, TrendingDown, AlertTriangle, Shield, CheckCircle2, ChevronRight, Clock, Target } from 'lucide-react';
import { predictionService } from '../services/predictionService';
import api from '../services/api';
import type { AssetRiskForecastResponse } from '../types/prediction';

export function RiskPrediction() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [predictionData, setPredictionData] = useState<AssetRiskForecastResponse | null>(null);
  const [selectedHorizon, setSelectedHorizon] = useState<7 | 30 | 90>(30);

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        setLoading(true);
        // Step 1: Get the org's first asset to demo asset-level prediction
        const assetsRes = await api.get<{ items: { id: string }[] }>('/api/v1/assets/');
        if (assetsRes.items && assetsRes.items.length > 0) {
          const assetId = assetsRes.items[0].id;
          
          // Generate/Fetch prediction for the asset
          try {
            const data = await predictionService.calculateAssetPrediction(assetId);
            setPredictionData(data);
            setError(null);
          } catch (e: any) {
            if (e.response && e.response.status === 422) {
              setError("Not enough historical data for reliable forecasting. Please generate history first.");
            } else {
              setError("Failed to generate prediction.");
            }
          }
        } else {
          setError("No assets found in organization to run predictions on.");
        }
      } catch (err) {
        console.error(err);
        setError("Error connecting to backend API.");
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Activity className="h-8 w-8 animate-pulse text-indigo-500" />
          <p className="text-sm text-slate-400">Loading ML Models & Generating Forecast...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center">
          <AlertTriangle className="mx-auto mb-4 h-12 w-12 text-red-400" />
          <h2 className="mb-2 text-lg font-semibold text-white">Prediction Unavailable</h2>
          <p className="text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  if (!predictionData) return null;

  const currentPrediction = predictionData.forecasts[selectedHorizon];

  return (
    <div className="mx-auto max-w-6xl p-6 lg:p-8">
      <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Target className="h-6 w-6 text-indigo-400" />
            AI-Powered Risk Forecast
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Machine learning projection based on asset telemetry, threat intel, and historical risk records.
          </p>
        </div>
        
        {/* Horizon Selector */}
        <div className="flex rounded-lg bg-slate-800 p-1">
          {[7, 30, 90].map((h) => (
            <button
              key={h}
              onClick={() => setSelectedHorizon(h as 7 | 30 | 90)}
              className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                selectedHorizon === h 
                ? 'bg-indigo-500 text-white shadow-sm' 
                : 'text-slate-400 hover:text-white'
              }`}
            >
              {h} Days
            </button>
          ))}
        </div>
      </div>

      {/* Main Forecast Overview */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6 backdrop-blur-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Current Risk</span>
            <Shield className="h-5 w-5 text-slate-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-white">{predictionData.current_risk.toFixed(1)}</span>
            <span className="text-sm text-slate-500">/ 100</span>
          </div>
        </div>

        <div className="rounded-xl border border-indigo-500/30 bg-indigo-500/10 p-6 backdrop-blur-sm relative overflow-hidden">
          <div className="absolute right-0 top-0 opacity-10">
            {currentPrediction.trend === 'increasing' ? (
              <TrendingUp className="h-24 w-24 translate-x-4 -translate-y-4" />
            ) : currentPrediction.trend === 'decreasing' ? (
              <TrendingDown className="h-24 w-24 translate-x-4 -translate-y-4" />
            ) : (
              <Activity className="h-24 w-24 translate-x-4 -translate-y-4" />
            )}
          </div>
          <div className="mb-2 flex items-center justify-between relative z-10">
            <span className="text-sm font-medium text-indigo-300">Forecasted Risk ({selectedHorizon}d)</span>
          </div>
          <div className="flex items-baseline gap-3 relative z-10">
            <span className="text-4xl font-bold text-white">
              {currentPrediction.predicted_risk.toFixed(1)}
            </span>
            <div className={`flex items-center text-sm font-medium ${
              currentPrediction.trend === 'increasing' ? 'text-red-400' :
              currentPrediction.trend === 'decreasing' ? 'text-emerald-400' : 'text-slate-400'
            }`}>
              {currentPrediction.trend === 'increasing' && <TrendingUp className="mr-1 h-4 w-4" />}
              {currentPrediction.trend === 'decreasing' && <TrendingDown className="mr-1 h-4 w-4" />}
              {currentPrediction.trend === 'increasing' ? '+' : ''}
              {(currentPrediction.predicted_risk - predictionData.current_risk).toFixed(1)}
            </div>
          </div>
          <div className="mt-4 text-xs text-indigo-200/60 relative z-10">
            Expected Range: {currentPrediction.lower_bound.toFixed(1)} – {currentPrediction.upper_bound.toFixed(1)}
          </div>
        </div>

        <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6 backdrop-blur-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Prediction Confidence</span>
            <CheckCircle2 className={`h-5 w-5 ${currentPrediction.confidence >= 80 ? 'text-emerald-500' : 'text-amber-500'}`} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-white">{currentPrediction.confidence.toFixed(0)}%</span>
          </div>
          <div className="mt-4 w-full rounded-full bg-slate-800 h-1.5">
            <div 
              className={`h-1.5 rounded-full ${currentPrediction.confidence >= 80 ? 'bg-emerald-500' : 'bg-amber-500'}`} 
              style={{ width: `${currentPrediction.confidence}%` }}
            />
          </div>
        </div>
      </div>

      {/* Model Transparency & Financial impact */}
      <div className="grid gap-6 md:grid-cols-2 mb-8">
        
        {/* Model Info */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">Model Transparency</h3>
          <div className="space-y-4">
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-sm text-slate-400">Algorithm</span>
              <span className="text-sm font-medium text-white">{currentPrediction.model_name.replace(/_/g, ' ')}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-sm text-slate-400">Version</span>
              <span className="text-sm font-medium text-white">{currentPrediction.model_version}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-sm text-slate-400">Last Calculated</span>
              <span className="text-sm font-medium text-white">
                {new Date(currentPrediction.prediction_timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Drivers */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 p-6">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">Contributing Drivers</h3>
          {predictionData.drivers.length > 0 ? (
            <div className="space-y-3">
              {predictionData.drivers.map((driver, idx) => (
                <div key={idx} className="rounded-lg bg-slate-800/50 p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white capitalize">{driver.feature.replace(/_/g, ' ')}</span>
                    <span className="text-xs text-slate-400">Weight: {(driver.importance * 100).toFixed(0)}%</span>
                  </div>
                  <p className="text-xs text-slate-400">{driver.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex h-32 items-center justify-center text-sm text-slate-500">
              No specific drivers extracted for this model.
            </div>
          )}
        </div>
      </div>

      {/* Financial Forecast */}
      {currentPrediction.predicted_financial_exposure !== null && currentPrediction.predicted_financial_exposure !== undefined && (
        <div className="mb-8 rounded-xl border border-slate-700/50 bg-slate-900/60 p-6">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">Forecasted Financial Exposure</h3>
          <div className="flex flex-col md:flex-row md:items-center gap-8">
            <div>
              <p className="text-sm text-slate-400 mb-1">Current Expected Annual Loss</p>
              <p className="text-2xl font-bold text-white">
                ₹{((predictionData.current_financial_exposure || 0) / 10000000).toFixed(2)} Cr
              </p>
            </div>
            <ChevronRight className="hidden md:block h-8 w-8 text-slate-600" />
            <div>
              <p className="text-sm text-indigo-300 mb-1">Forecasted Expected Annual Loss ({selectedHorizon}d)</p>
              <p className="text-2xl font-bold text-white">
                ₹{(currentPrediction.predicted_financial_exposure / 10000000).toFixed(2)} Cr
              </p>
            </div>
            <div className="ml-auto">
              <p className="text-xs text-slate-500">
                Range: ₹{((currentPrediction.financial_lower_bound || 0) / 10000000).toFixed(2)} Cr - ₹{((currentPrediction.financial_upper_bound || 0) / 10000000).toFixed(2)} Cr
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="rounded-lg bg-slate-800/30 p-4 border border-slate-700/50 flex items-start gap-3">
        <Clock className="h-5 w-5 text-slate-400 mt-0.5 shrink-0" />
        <p className="text-sm text-slate-400">
          <strong className="text-slate-300">Disclaimer:</strong> Forecasts are model-based estimates derived from historical and current cybersecurity data. 
          They are not guarantees of future incidents or attack probabilities.
        </p>
      </div>

    </div>
  );
}
