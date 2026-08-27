import { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';

type ConnectionStatus = 'checking' | 'connected' | 'unavailable';

/**
 * Hook to monitor backend connectivity.
 * Calls the health endpoint on mount and returns the current status.
 */
export function useBackendStatus() {
  const [status, setStatus] = useState<ConnectionStatus>('checking');

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const response = await checkHealth();
        if (!cancelled && response.status === 'healthy') {
          setStatus('connected');
        }
      } catch {
        if (!cancelled) {
          setStatus('unavailable');
        }
      }
    }

    check();

    return () => {
      cancelled = true;
    };
  }, []);

  return status;
}
