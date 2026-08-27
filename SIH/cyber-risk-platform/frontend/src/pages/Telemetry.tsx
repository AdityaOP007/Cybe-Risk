import React, { useState, useEffect, useCallback } from 'react';
import { Activity, RefreshCw, Filter, Search } from 'lucide-react';
import { telemetryService } from '../services/telemetryService';
import type { TelemetryEvent, TelemetryStats, TelemetryEventFilters } from '../types/telemetry';
import { TelemetryTable } from '../components/telemetry/TelemetryTable';
import { TelemetryDetailDrawer } from '../components/telemetry/TelemetryDetailDrawer';
import { api } from '../services/api';

export const Telemetry: React.FC = () => {
  const [events, setEvents] = useState<TelemetryEvent[]>([]);
  const [stats, setStats] = useState<TelemetryStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const [selectedEvent, setSelectedEvent] = useState<TelemetryEvent | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  
  const [filters, setFilters] = useState<TelemetryEventFilters>({
    page: 1,
    page_size: 50,
  });
  
  const [organizationId, setOrganizationId] = useState<string | null>(null);

  // Temporary logic to get the default org
  useEffect(() => {
    const fetchOrg = async () => {
      try {
        const orgs = await api.get<any[]>('/api/v1/organizations/');
        if (orgs && orgs.length > 0) {
          setOrganizationId(orgs[0].id);
        }
      } catch (error) {
        console.error("Failed to fetch organization:", error);
      }
    };
    fetchOrg();
  }, []);

  const loadData = useCallback(async (isBackground = false) => {
    if (!organizationId) return;
    
    if (!isBackground) setIsLoading(true);
    else setIsRefreshing(true);

    try {
      const [eventsData, statsData] = await Promise.all([
        telemetryService.getTelemetryEvents({ ...filters, organization_id: organizationId }),
        telemetryService.getTelemetryStats(organizationId)
      ]);
      setEvents(eventsData.items);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load telemetry data:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [filters, organizationId]);

  useEffect(() => {
    if (organizationId) {
      loadData();
    }
  }, [organizationId, filters.page, filters.severity, filters.source]);

  // Polling mechanism
  useEffect(() => {
    if (!organizationId) return;
    const intervalId = setInterval(() => {
      loadData(true);
    }, 30000); // Poll every 30 seconds
    
    return () => clearInterval(intervalId);
  }, [loadData, organizationId]);

  const handleRowClick = (event: TelemetryEvent) => {
    setSelectedEvent(event);
    setIsDrawerOpen(true);
  };

  const handleFilterChange = (key: keyof TelemetryEventFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-indigo-500" />
            Security Telemetry
          </h1>
          <p className="text-gray-400 text-sm mt-1">Real-time event stream from security controls and sensors</p>
        </div>
        <button 
          onClick={() => loadData(true)}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
          {isRefreshing ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <div className="bg-gray-800/40 p-4 rounded-xl border border-gray-700/50 flex flex-col justify-center items-center text-center">
             <span className="text-2xl font-bold text-white">{stats.total_events}</span>
             <span className="text-xs text-gray-400 uppercase tracking-wide mt-1">Total Events</span>
          </div>
          <div className="bg-red-500/10 p-4 rounded-xl border border-red-500/20 flex flex-col justify-center items-center text-center">
             <span className="text-2xl font-bold text-red-500">{stats.critical_events}</span>
             <span className="text-xs text-red-400/80 uppercase tracking-wide mt-1">Critical</span>
          </div>
          <div className="bg-orange-500/10 p-4 rounded-xl border border-orange-500/20 flex flex-col justify-center items-center text-center">
             <span className="text-2xl font-bold text-orange-500">{stats.high_events}</span>
             <span className="text-xs text-orange-400/80 uppercase tracking-wide mt-1">High</span>
          </div>
          <div className="bg-yellow-500/10 p-4 rounded-xl border border-yellow-500/20 flex flex-col justify-center items-center text-center">
             <span className="text-2xl font-bold text-yellow-500">{stats.medium_events}</span>
             <span className="text-xs text-yellow-400/80 uppercase tracking-wide mt-1">Medium</span>
          </div>
          <div className="bg-blue-500/10 p-4 rounded-xl border border-blue-500/20 flex flex-col justify-center items-center text-center">
             <span className="text-2xl font-bold text-blue-500">{stats.low_events}</span>
             <span className="text-xs text-blue-400/80 uppercase tracking-wide mt-1">Low</span>
          </div>
          <div className="bg-gray-500/10 p-4 rounded-xl border border-gray-500/20 flex flex-col justify-center items-center text-center">
             <span className="text-2xl font-bold text-gray-400">{stats.informational_events}</span>
             <span className="text-xs text-gray-500 uppercase tracking-wide mt-1">Info</span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-4 p-4 bg-gray-800/40 rounded-xl border border-gray-700/50">
        <div className="flex-1 relative">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            type="text"
            placeholder="Search telemetry..."
            className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
        
        <select 
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
          value={filters.severity || ''}
          onChange={(e) => handleFilterChange('severity', e.target.value || undefined)}
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="informational">Informational</option>
        </select>

        <select 
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
          value={filters.source || ''}
          onChange={(e) => handleFilterChange('source', e.target.value || undefined)}
        >
          <option value="">All Sources</option>
          <option value="siem">SIEM</option>
          <option value="edr">EDR</option>
          <option value="firewall">Firewall</option>
          <option value="ids">IDS</option>
          <option value="iam">IAM</option>
          <option value="cloud">Cloud</option>
          <option value="application">Application</option>
        </select>
      </div>

      <TelemetryTable 
        events={events} 
        isLoading={isLoading} 
        onRowClick={handleRowClick}
      />

      <TelemetryDetailDrawer 
        event={selectedEvent} 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
      />
    </div>
  );
};
