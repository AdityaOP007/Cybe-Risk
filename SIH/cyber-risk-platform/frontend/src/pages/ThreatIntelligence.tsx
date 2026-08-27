import React, { useState, useEffect, useCallback } from 'react';
import { ShieldAlert, Globe, Network, Filter } from 'lucide-react';
import { ThreatTable } from '../components/threat/ThreatTable';
import { ThreatDetailDrawer } from '../components/threat/ThreatDetailDrawer';
import { threatIntelligenceService } from '../services/threatIntelligenceService';
import type { ThreatIntelligenceRecord, ThreatIntelligenceStats } from '../types/threatIntelligence';

export const ThreatIntelligence: React.FC = () => {
  const [stats, setStats] = useState<ThreatIntelligenceStats | null>(null);
  const [threats, setThreats] = useState<ThreatIntelligenceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedThreat, setSelectedThreat] = useState<ThreatIntelligenceRecord | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const fetchStats = async () => {
    try {
      const data = await threatIntelligenceService.getThreatStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load threat stats', err);
    }
  };

  const fetchThreats = useCallback(async () => {
    setLoading(true);
    try {
      const data = await threatIntelligenceService.getThreats({
        search,
        severity: severityFilter,
        intelligence_type: typeFilter,
      });
      setThreats(data.items);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load threat intelligence');
    } finally {
      setLoading(false);
    }
  }, [search, severityFilter, typeFilter]);

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    fetchThreats();
  }, [fetchThreats]);

  const handleRowClick = (threat: ThreatIntelligenceRecord) => {
    setSelectedThreat(threat);
    setIsDrawerOpen(true);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold leading-tight text-white flex items-center gap-3">
            <Globe className="w-8 h-8 text-indigo-500" />
            Global Threat Intelligence
          </h1>
          <p className="mt-2 text-sm text-gray-400">
            Monitor active campaigns, known exploited vulnerabilities, and indicators of compromise.
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="rounded-xl bg-gray-900 border border-gray-800 p-5 shadow-lg relative overflow-hidden group hover:border-red-500/50 transition-colors">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <ShieldAlert className="w-16 h-16 text-red-500" />
            </div>
            <p className="text-sm font-medium text-gray-400 mb-1 z-10 relative">Known Exploited</p>
            <p className="text-3xl font-bold text-red-500 z-10 relative">{stats.known_exploited}</p>
          </div>
          
          <div className="rounded-xl bg-gray-900 border border-gray-800 p-5 shadow-lg relative overflow-hidden group hover:border-orange-500/50 transition-colors">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <ShieldAlert className="w-16 h-16 text-orange-500" />
            </div>
            <p className="text-sm font-medium text-gray-400 mb-1 z-10 relative">Critical Threats</p>
            <p className="text-3xl font-bold text-orange-500 z-10 relative">{stats.critical}</p>
          </div>

          <div className="rounded-xl bg-gray-900 border border-gray-800 p-5 shadow-lg relative overflow-hidden group hover:border-blue-500/50 transition-colors">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Network className="w-16 h-16 text-blue-500" />
            </div>
            <p className="text-sm font-medium text-gray-400 mb-1 z-10 relative">Active Indicators (IOCs)</p>
            <p className="text-3xl font-bold text-blue-500 z-10 relative">{stats.indicators}</p>
          </div>

          <div className="rounded-xl bg-gray-900 border border-gray-800 p-5 shadow-lg relative overflow-hidden group hover:border-indigo-500/50 transition-colors">
            <p className="text-sm font-medium text-gray-400 mb-1 z-10 relative">Total Intel Records</p>
            <p className="text-3xl font-bold text-white z-10 relative">{stats.total_threats}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 flex flex-col md:flex-row gap-4 bg-gray-900/50 p-4 rounded-lg border border-gray-800 items-end">
        <div className="w-full md:w-64">
          <label className="block text-xs font-medium text-gray-400 mb-1">Search Intel</label>
          <input
            type="text"
            placeholder="CVE-2024-..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="block w-full rounded-md border-0 bg-gray-800 py-2 text-white shadow-sm ring-1 ring-inset ring-gray-700 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6"
          />
        </div>
        
        <div className="w-full md:w-48">
          <label className="block text-xs font-medium text-gray-400 mb-1">Severity</label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="block w-full rounded-md border-0 bg-gray-800 py-2 text-white shadow-sm ring-1 ring-inset ring-gray-700 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="w-full md:w-48">
          <label className="block text-xs font-medium text-gray-400 mb-1">Intel Type</label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="block w-full rounded-md border-0 bg-gray-800 py-2 text-white shadow-sm ring-1 ring-inset ring-gray-700 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6"
          >
            <option value="">All Types</option>
            <option value="vulnerability">Vulnerability (CVE)</option>
            <option value="campaign">Campaign</option>
            <option value="actor">Threat Actor</option>
            <option value="malware">Malware</option>
          </select>
        </div>
        
        <div>
          <button 
            onClick={fetchThreats}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 px-4 rounded-md transition-colors flex items-center gap-2 text-sm"
          >
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
      </div>

      {/* Main Table */}
      {error ? (
        <div className="rounded-lg bg-red-500/10 p-4 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      ) : (
        <ThreatTable 
          threats={threats} 
          isLoading={loading} 
          onRowClick={handleRowClick}
        />
      )}

      {/* Side Drawer */}
      <ThreatDetailDrawer 
        threat={selectedThreat}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  );
};
