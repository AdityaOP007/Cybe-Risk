import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, FileWarning, RefreshCw, CheckCircle2, XCircle, Network
} from 'lucide-react';
import type {  
  ComplianceFramework, FrameworkAssessmentSummary, ComplianceGap, CrosswalkResponse 
 } from "../types/compliance";
import { 
  getFrameworks, getFrameworkSummary, getGaps, assessFramework, getControlCrosswalk
} from '../services/complianceService';

const Compliance: React.FC = () => {
  const [frameworks, setFrameworks] = useState<ComplianceFramework[]>([]);
  const [summaries, setSummaries] = useState<Record<string, FrameworkAssessmentSummary>>({});
  const [gaps, setGaps] = useState<ComplianceGap[]>([]);
  const [loading, setLoading] = useState(true);
  const [assessing, setAssessing] = useState<string | null>(null);
  const [, setSelectedControl] = useState<string | null>(null);
  const [crosswalk, setCrosswalk] = useState<CrosswalkResponse | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [fws, gapsData] = await Promise.all([
        getFrameworks(),
        getGaps()
      ]);
      setFrameworks(fws);
      setGaps(gapsData);
      
      const sums: Record<string, FrameworkAssessmentSummary> = {};
      for (const fw of fws) {
        try {
          sums[fw.id] = await getFrameworkSummary(fw.id);
        } catch (e) {
          console.error(`Failed to load summary for ${fw.id}`, e);
        }
      }
      setSummaries(sums);
      
      if (gapsData.length > 0 && gapsData[0].control_id) {
         handleViewCrosswalk(gapsData[0].control_id);
      }
    } catch (error) {
      console.error("Error fetching compliance data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssess = async (frameworkId: string) => {
    try {
      setAssessing(frameworkId);
      const newSummary = await assessFramework(frameworkId);
      setSummaries(prev => ({ ...prev, [frameworkId]: newSummary }));
      
      // Refresh gaps too
      const newGaps = await getGaps();
      setGaps(newGaps);
    } catch (error) {
      console.error("Error assessing framework:", error);
    } finally {
      setAssessing(null);
    }
  };

  const handleViewCrosswalk = async (controlId: string) => {
    setSelectedControl(controlId);
    try {
      const data = await getControlCrosswalk(controlId);
      setCrosswalk(data);
    } catch (e) {
      console.error("Error loading crosswalk", e);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="h-8 w-8 animate-spin text-indigo-500" />
          <p className="text-gray-400">Loading regulatory posture...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Compliance & Regulatory Posture</h1>
          <p className="text-gray-400">Continuous evidence-based compliance and cross-framework mapping.</p>
        </div>
        <button 
          onClick={fetchData}
          className="flex items-center gap-2 rounded-lg bg-[#1e293b] px-4 py-2 text-sm font-medium text-white hover:bg-[#2d3b4e]"
        >
          <RefreshCw className="h-4 w-4" /> Refresh All
        </button>
      </div>

      {/* Framework Summaries */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {frameworks.map(fw => {
          const summary = summaries[fw.id];
          return (
            <div key={fw.id} className="rounded-xl border border-gray-800 bg-[#0f172a] p-6 shadow-xl">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-white">{fw.name}</h3>
                  <p className="text-xs text-gray-400">{fw.jurisdiction}</p>
                </div>
                <button 
                  onClick={() => handleAssess(fw.id)}
                  disabled={assessing === fw.id}
                  className="rounded bg-indigo-500/10 p-2 text-indigo-400 hover:bg-indigo-500/20 disabled:opacity-50"
                  title="Assess Framework"
                >
                  <RefreshCw className={`h-4 w-4 ${assessing === fw.id ? 'animate-spin' : ''}`} />
                </button>
              </div>
              
              {summary ? (
                <>
                  <div className="mb-4 flex items-end gap-2">
                    <span className="text-4xl font-bold text-white">{summary.coverage_percentage}%</span>
                    <span className="mb-1 text-sm text-gray-400">Coverage</span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="flex items-center gap-1 text-emerald-400"><CheckCircle2 className="h-4 w-4"/> Compliant</span>
                      <span className="font-medium text-white">{summary.compliant}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="flex items-center gap-1 text-yellow-400"><AlertTriangle className="h-4 w-4"/> Partial</span>
                      <span className="font-medium text-white">{summary.partially_compliant}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="flex items-center gap-1 text-orange-400"><FileWarning className="h-4 w-4"/> Missing Evidence</span>
                      <span className="font-medium text-white">{summary.insufficient_evidence}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="flex items-center gap-1 text-red-400"><XCircle className="h-4 w-4"/> Non-Compliant</span>
                      <span className="font-medium text-white">{summary.non_compliant}</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex h-32 items-center justify-center text-sm text-gray-500">
                  Not Assessed
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Gaps Table */}
        <div className="rounded-xl border border-gray-800 bg-[#0f172a] lg:col-span-2">
          <div className="border-b border-gray-800 p-6">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-white">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              Actionable Compliance Gaps
            </h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-300">
                <thead className="bg-[#1e293b] text-xs uppercase text-gray-400">
                  <tr>
                    <th className="px-4 py-3">Gap Type</th>
                    <th className="px-4 py-3">Description</th>
                    <th className="px-4 py-3">Severity</th>
                    <th className="px-4 py-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {gaps.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-4 text-center text-gray-500">No open compliance gaps.</td>
                    </tr>
                  ) : (
                    gaps.map(gap => (
                      <tr key={gap.id} className="hover:bg-gray-800/50">
                        <td className="px-4 py-3 font-medium text-white">{gap.gap_type.replace('_', ' ')}</td>
                        <td className="px-4 py-3">{gap.description}</td>
                        <td className="px-4 py-3">
                           <span className={`rounded-full px-2 py-1 text-xs font-semibold ${
                            gap.severity === 'high' ? 'bg-red-500/10 text-red-500' :
                            gap.severity === 'medium' ? 'bg-orange-500/10 text-orange-500' :
                            'bg-yellow-500/10 text-yellow-500'
                          }`}>
                            {gap.severity}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {gap.control_id && (
                             <button 
                              onClick={() => handleViewCrosswalk(gap.control_id!)}
                              className="text-indigo-400 hover:text-indigo-300"
                            >
                              Crosswalk
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Crosswalk Visualizer */}
        <div className="rounded-xl border border-gray-800 bg-[#0f172a]">
          <div className="border-b border-gray-800 p-6">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-white">
              <Network className="h-5 w-5 text-indigo-500" />
              Control Crosswalk
            </h2>
            <p className="mt-1 text-xs text-gray-400">Multi-framework mapping for selected control.</p>
          </div>
          <div className="p-6 space-y-6">
            {crosswalk ? Object.entries(crosswalk).map(([fwName, mappings]) => (
               <div key={fwName} className="rounded-lg bg-[#1e293b] p-4">
                  <h4 className="mb-2 font-semibold text-white">{fwName}</h4>
                  <div className="space-y-2">
                    {mappings.map((m, idx) => (
                      <div key={idx} className="flex items-start justify-between text-sm">
                        <div className="flex-1">
                          <span className="font-mono text-indigo-400">{m.requirement_id}</span>
                          <p className="text-gray-300">{m.title}</p>
                        </div>
                        <div className="ml-4 text-right">
                          <span className={`inline-block rounded px-2 py-0.5 text-xs ${
                            m.mapping_type === 'direct' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'
                          }`}>
                            {m.mapping_type}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
               </div>
            )) : (
              <div className="text-center text-sm text-gray-500 py-10">
                Select a control from the gaps table to view its cross-framework mapping.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Compliance;
