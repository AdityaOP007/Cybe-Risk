interface StatusBadgeProps {
  status: 'checking' | 'connected' | 'unavailable';
}

const statusConfig = {
  checking: {
    label: 'Checking...',
    dotClass: 'bg-amber-400 animate-pulse',
    textClass: 'text-amber-400',
  },
  connected: {
    label: 'Connected',
    dotClass: 'bg-emerald-400',
    textClass: 'text-emerald-400',
  },
  unavailable: {
    label: 'Unavailable',
    dotClass: 'bg-red-400',
    textClass: 'text-red-400',
  },
} as const;

/**
 * Displays a colored status indicator with label.
 */
export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <div className="flex items-center gap-2">
      <span className={`inline-block h-2.5 w-2.5 rounded-full ${config.dotClass}`} />
      <span className={`text-sm font-medium ${config.textClass}`}>
        {config.label}
      </span>
    </div>
  );
}
