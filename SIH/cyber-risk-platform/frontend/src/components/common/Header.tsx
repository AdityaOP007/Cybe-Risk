import { StatusBadge } from './StatusBadge';

interface HeaderProps {
  backendStatus: 'checking' | 'connected' | 'unavailable';
}

/**
 * Application header with logo/title and backend status indicator.
 */
export function Header({ backendStatus }: HeaderProps) {
  return (
    <header className="border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20">
              <svg
                className="h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z"
                />
              </svg>
            </div>
            <h1 className="text-lg font-semibold tracking-tight text-white">
              Cyber Risk Platform
            </h1>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
            <a href="/" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Dashboard</a>
            <a href="/assets" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Asset Inventory</a>
            <a href="/telemetry" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Security Telemetry</a>
            <a href="/threat-intel" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Threat Intelligence</a>
            <a href="/financial-risk" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Financial Risk</a>
            <a href="/risk-prediction" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Risk Forecast</a>
            <a href="/recommendations" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Mitigations</a>
            <a href="/optimization" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Budget Optimization</a>
            <a href="/compliance" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Compliance</a>
          </nav>
        </div>

        {/* Backend Status */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">Backend Status</span>
          <StatusBadge status={backendStatus} />
        </div>
      </div>
    </header>
  );
}
