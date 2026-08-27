import React from 'react';

interface RiskScoreMeterProps {
  score: number;
  level: string;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskScoreMeter: React.FC<RiskScoreMeterProps> = ({ score, level, size = 'md' }) => {
  // SVG setup
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  // Score is 0-100, we want to map this to the circle circumference
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  // Colors based on risk level
  const getColorClass = (l: string) => {
    switch(l.toLowerCase()) {
      case 'critical': return 'text-red-500';
      case 'high': return 'text-orange-500';
      case 'medium': return 'text-amber-500';
      case 'low': return 'text-green-500';
      default: return 'text-slate-500';
    }
  };

  const getBgClass = (l: string) => {
    switch(l.toLowerCase()) {
      case 'critical': return 'text-red-500/20';
      case 'high': return 'text-orange-500/20';
      case 'medium': return 'text-amber-500/20';
      case 'low': return 'text-green-500/20';
      default: return 'text-slate-500/20';
    }
  };

  const sizeClasses = {
    sm: { wrapper: 'w-24 h-24', text: 'text-xl', label: 'text-xs' },
    md: { wrapper: 'w-32 h-32', text: 'text-3xl', label: 'text-sm' },
    lg: { wrapper: 'w-48 h-48', text: 'text-5xl', label: 'text-base' },
  };

  const s = sizeClasses[size];

  return (
    <div className={`relative flex flex-col items-center justify-center ${s.wrapper}`}>
      {/* SVG Circle */}
      <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
        {/* Background track */}
        <circle
          className={getBgClass(level)}
          strokeWidth="8"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx="50"
          cy="50"
        />
        {/* Progress track */}
        <circle
          className={`${getColorClass(level)} transition-all duration-1000 ease-out`}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx="50"
          cy="50"
        />
      </svg>
      {/* Score Text */}
      <div className="absolute flex flex-col items-center justify-center">
        <span className={`font-bold text-white ${s.text}`}>{score.toFixed(0)}</span>
        <span className={`uppercase font-medium tracking-wider mt-1 ${getColorClass(level)} ${s.label}`}>
          {level}
        </span>
      </div>
    </div>
  );
};
