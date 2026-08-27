import React from 'react';
import { X } from 'lucide-react';
import { format } from 'date-fns';
import type { TelemetryEvent } from '../../types/telemetry';

interface TelemetryDetailDrawerProps {
  event: TelemetryEvent | null;
  isOpen: boolean;
  onClose: () => void;
}

export const TelemetryDetailDrawer: React.FC<TelemetryDetailDrawerProps> = ({ event, isOpen, onClose }) => {
  if (!isOpen || !event) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />
      
      <div className="fixed inset-y-0 right-0 w-full max-w-xl bg-gray-900 border-l border-gray-800 shadow-2xl z-50 flex flex-col transform transition-transform duration-300">
        <div className="flex items-center justify-between p-6 border-b border-gray-800 bg-gray-900/95 sticky top-0">
          <h2 className="text-xl font-semibold text-white">Event Details</h2>
          <button 
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Time</p>
              <p className="text-sm text-gray-200">{format(new Date(event.occurred_at), 'PP pp')}</p>
            </div>
            
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Severity</p>
              <p className="text-sm font-medium capitalize">{event.severity}</p>
            </div>
            
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Source</p>
              <p className="text-sm uppercase">{event.source}</p>
            </div>

            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Event Type</p>
              <p className="text-sm capitalize">{event.event_type.replace(/_/g, ' ')}</p>
            </div>
          </div>

          <div className="bg-gray-800/50 p-4 rounded-lg">
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Message</p>
            <p className="text-sm text-gray-200">{event.message || 'No message provided'}</p>
          </div>

          <div className="bg-gray-800/50 p-4 rounded-lg">
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Source Event ID</p>
            <p className="text-sm text-gray-200 font-mono">{event.source_event_id || 'N/A'}</p>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-300 mb-2">Raw Event Data</h3>
            <div className="bg-[#0d1117] border border-gray-800 rounded-lg p-4 overflow-x-auto">
              <pre className="text-xs text-green-400 font-mono">
                {JSON.stringify(event.event_data, null, 2)}
              </pre>
            </div>
          </div>
          
          <div className="text-xs text-gray-500 pt-4 border-t border-gray-800">
            Internal ID: {event.id} <br/>
            Ingested: {format(new Date(event.created_at), 'PP pp')}
          </div>
        </div>
      </div>
    </>
  );
};
