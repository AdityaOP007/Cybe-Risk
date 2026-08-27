import React from 'react';
import { DashboardAlert } from '../../types/dashboard';
import { Bell, Check, X, ShieldAlert } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface ExecutiveAlertsProps {
  alerts: DashboardAlert[];
  onAcknowledge: (id: string) => void;
}

export const ExecutiveAlerts: React.FC<ExecutiveAlertsProps> = ({ alerts, onAcknowledge }) => {
  if (alerts.length === 0) return null;

  return (
    <div className="bg-[#0f172a] rounded-xl border border-red-500/30 shadow-md mb-8 overflow-hidden">
      <div className="bg-red-500/10 px-5 py-3 border-b border-red-500/20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="h-4 w-4 text-red-400" />
          <h3 className="text-sm font-semibold text-red-400 uppercase tracking-wider">Attention Required</h3>
        </div>
        <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded-full font-medium">
          {alerts.length}
        </span>
      </div>
      <div className="divide-y divide-gray-800">
        {alerts.map((alert) => (
          <div key={alert.id} className="p-4 flex items-start gap-4">
            <div className="mt-1">
              <ShieldAlert className="h-5 w-5 text-red-500" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <h4 className="text-sm font-semibold text-white">{alert.title}</h4>
                <span className="text-xs text-gray-500">
                  {formatDistanceToNow(new Date(alert.first_seen), { addSuffix: true })}
                </span>
              </div>
              <p className="text-sm text-gray-400 mb-2">{alert.reason}</p>
              <div className="flex items-center gap-3">
                <button 
                  onClick={() => onAcknowledge(alert.id)}
                  className="text-xs font-medium text-gray-400 hover:text-white flex items-center gap-1"
                >
                  <Check className="h-3 w-3" /> Acknowledge
                </button>
                {alert.action_link && (
                  <button className="text-xs font-medium text-indigo-400 hover:text-indigo-300">
                    View Details
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
