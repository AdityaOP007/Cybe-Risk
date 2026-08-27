import React from 'react';

export const CriticalityBadge: React.FC<{ criticality: number }> = ({ criticality }) => {
  let label = 'Very Low';
  let colors = 'bg-slate-100 text-slate-800 border-slate-200';
  
  if (criticality >= 81) {
    label = 'Critical';
    colors = 'bg-red-500/10 text-red-500 border-red-500/20';
  } else if (criticality >= 61) {
    label = 'High';
    colors = 'bg-orange-500/10 text-orange-500 border-orange-500/20';
  } else if (criticality >= 41) {
    label = 'Medium';
    colors = 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
  } else if (criticality >= 21) {
    label = 'Low';
    colors = 'bg-blue-500/10 text-blue-500 border-blue-500/20';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors}`}>
      {label} ({criticality})
    </span>
  );
};

export const EnvironmentBadge: React.FC<{ env: string }> = ({ env }) => {
  let colors = 'bg-slate-100 text-slate-800 border-slate-200';
  
  switch(env.toLowerCase()) {
    case 'production':
      colors = 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      break;
    case 'staging':
      colors = 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      break;
    case 'development':
      colors = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      break;
    case 'testing':
      colors = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      break;
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${colors}`}>
      {env}
    </span>
  );
};

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  let colors = 'bg-slate-100 text-slate-800 border-slate-200';
  
  switch(status.toLowerCase()) {
    case 'active':
      colors = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      break;
    case 'inactive':
      colors = 'bg-slate-500/10 text-slate-400 border-slate-500/20';
      break;
    case 'maintenance':
      colors = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      break;
    case 'retired':
      colors = 'bg-red-500/10 text-red-400 border-red-500/20';
      break;
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${colors}`}>
      {status}
    </span>
  );
};

export const ExposureBadge: React.FC<{ exposed: boolean }> = ({ exposed }) => {
  if (exposed) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-red-500/10 text-red-400 border-red-500/20">
        Public
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-slate-800 text-slate-300 border-slate-700">
      Internal
    </span>
  );
};
