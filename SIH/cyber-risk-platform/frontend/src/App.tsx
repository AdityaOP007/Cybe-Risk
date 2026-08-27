import { Header } from './components/common/Header';
import { useBackendStatus } from './hooks/useBackendStatus';

function App() {
  const backendStatus = useBackendStatus();

  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <Header backendStatus={backendStatus} />

      {/* Main Content */}
      <main className="flex flex-1 items-center justify-center px-6">
        <div className="text-center">
          {/* Hero section */}
          <div className="mb-8">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-2xl shadow-indigo-500/30">
              <svg
                className="h-10 w-10 text-white"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z"
                />
              </svg>
            </div>
            <h2 className="mb-3 text-4xl font-bold tracking-tight text-white">
              Cyber Risk Platform
            </h2>
            <p className="mx-auto max-w-lg text-lg text-slate-400">
              AI-powered cyber risk quantification and decision intelligence
              for modern enterprises.
            </p>
          </div>

          {/* Status Card */}
          <div className="mx-auto max-w-sm rounded-xl border border-slate-700/50 bg-slate-900/60 p-6 shadow-xl backdrop-blur-sm">
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

          {/* Module info */}
          <p className="mt-8 text-xs text-slate-500">
            Module 01 — Project Foundation
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
