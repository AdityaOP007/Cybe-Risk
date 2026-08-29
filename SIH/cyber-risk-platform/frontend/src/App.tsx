import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/common/Header';
import { useBackendStatus } from './hooks/useBackendStatus';
import { Assets } from './pages/Assets';
import { AssetDetails } from './pages/AssetDetails';
import { Telemetry } from './pages/Telemetry';
import { ThreatIntelligence } from './pages/ThreatIntelligence';
import FinancialRisk from './pages/FinancialRisk';
import { RiskPrediction } from './pages/RiskPrediction';
import { Recommendations } from './pages/Recommendations';
import { BudgetOptimization } from './pages/BudgetOptimization';
import Compliance from './pages/Compliance';



import { ExecutiveDashboard } from './pages/ExecutiveDashboard';

function App() {
  const backendStatus = useBackendStatus();

  return (
    <Router>
      <div className="flex min-h-screen flex-col bg-slate-950">
        <Header backendStatus={backendStatus} />
        
        <Routes>
          <Route path="/" element={<ExecutiveDashboard />} />
          <Route path="/assets" element={<Assets />} />
          <Route path="/assets/:id" element={<AssetDetails />} />
          <Route path="/telemetry" element={<Telemetry />} />
          <Route path="/threat-intel" element={<ThreatIntelligence />} />
          <Route path="/financial-risk" element={<FinancialRisk />} />
          <Route path="/risk-prediction" element={<RiskPrediction />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/optimization" element={<BudgetOptimization />} />
          <Route path="/compliance" element={<Compliance />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
