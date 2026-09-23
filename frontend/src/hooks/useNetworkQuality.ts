'use client';

import { useState, useEffect } from 'react';

export type EffectiveConnectionType = '2g' | '3g' | '4g' | 'slow-2g' | 'offline' | 'unknown';

export interface NetworkState {
  isOnline: boolean;
  effectiveType: EffectiveConnectionType;
  saveData: boolean;
  isRuralMode: boolean; // Manual or auto-triggered 2G/3G mode
  toggleRuralMode: () => void;
  setRuralMode: (enabled: boolean) => void;
}

export function useNetworkQuality(): NetworkState {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [effectiveType, setEffectiveType] = useState<EffectiveConnectionType>('4g');
  const [saveData, setSaveData] = useState<boolean>(false);
  const [isRuralMode, setIsRuralModeState] = useState<boolean>(false);

  useEffect(() => {
    // Read persisted user preference for rural mode
    const stored = typeof window !== 'undefined' ? localStorage.getItem('yatri_rural_low_data_mode') : null;
    if (stored !== null) {
      setIsRuralModeState(stored === 'true');
    }

    const updateNetworkInfo = () => {
      const online = typeof navigator !== 'undefined' ? navigator.onLine : true;
      setIsOnline(online);

      if (!online) {
        setEffectiveType('offline');
        return;
      }

      // Check Network Information API if available (Chrome/Android)
      const conn = (navigator as unknown as { connection?: { effectiveType?: string; saveData?: boolean } }).connection;
      if (conn) {
        const type = (conn.effectiveType || '4g') as EffectiveConnectionType;
        setEffectiveType(type);
        setSaveData(!!conn.saveData);

        // Auto-enable Rural Low-Data mode if network is 2g or slow-2g or saveData is true
        if (stored === null && (type === '2g' || type === 'slow-2g' || type === '3g' || conn.saveData)) {
          setIsRuralModeState(true);
        }
      }
    };

    updateNetworkInfo();

    window.addEventListener('online', updateNetworkInfo);
    window.addEventListener('offline', updateNetworkInfo);

    const conn = (navigator as unknown as { connection?: { addEventListener?: (type: string, fn: () => void) => void } }).connection;
    if (conn && conn.addEventListener) {
      conn.addEventListener('change', updateNetworkInfo);
    }

    return () => {
      window.removeEventListener('online', updateNetworkInfo);
      window.removeEventListener('offline', updateNetworkInfo);
    };
  }, []);

  const toggleRuralMode = () => {
    const next = !isRuralMode;
    setIsRuralModeState(next);
    if (typeof window !== 'undefined') {
      localStorage.setItem('yatri_rural_low_data_mode', String(next));
    }
  };

  const setRuralMode = (enabled: boolean) => {
    setIsRuralModeState(enabled);
    if (typeof window !== 'undefined') {
      localStorage.setItem('yatri_rural_low_data_mode', String(enabled));
    }
  };

  return {
    isOnline,
    effectiveType,
    saveData,
    isRuralMode,
    toggleRuralMode,
    setRuralMode
  };
}
