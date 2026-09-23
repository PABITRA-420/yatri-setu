'use client';

import React, { useState, useEffect } from 'react';
import { WifiOff, Radio, CheckCircle, Info } from 'lucide-react';

export function OfflineDataToast() {
  const [show, setShow] = useState(false);
  const [mode, setMode] = useState<'offline' | 'fallback'>('fallback');

  useEffect(() => {
    // Check if network is offline or backend is fallback
    const updateOnline = () => {
      if (!navigator.onLine) {
        setMode('offline');
        setShow(true);
      }
    };

    window.addEventListener('offline', updateOnline);
    return () => window.removeEventListener('offline', updateOnline);
  }, []);

  if (!show) return null;

  return (
    <div className="fixed bottom-20 right-4 md:bottom-6 md:right-6 z-50 max-w-sm bg-stone-900/95 border border-amber-500/40 text-amber-200 px-4 py-3 rounded-2xl shadow-2xl backdrop-blur-xl flex items-center gap-3 animate-in slide-in-from-bottom duration-300">
      <div className="p-2 bg-amber-500/20 text-amber-400 rounded-xl shrink-0">
        <WifiOff className="w-4 h-4 animate-pulse" />
      </div>
      <div className="text-xs">
        <p className="font-bold text-amber-300">
          {mode === 'offline' ? 'Offline Mode Active' : 'Fallback Intelligence Active'}
        </p>
        <p className="text-stone-400 text-[11px] mt-0.5 leading-snug">
          Serving verified local cache & offline crowd baseline.
        </p>
      </div>
      <button
        onClick={() => setShow(false)}
        className="ml-auto text-stone-500 hover:text-white text-xs font-bold px-1.5 py-0.5"
      >
        ✕
      </button>
    </div>
  );
}
