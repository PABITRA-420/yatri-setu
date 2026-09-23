'use client';

import React, { useState } from 'react';
import { Signal, SignalLow, WifiOff, Zap, ShieldCheck } from 'lucide-react';
import { useNetworkQuality } from '@/hooks/useNetworkQuality';

export function RuralModeToggle() {
  const { isOnline, effectiveType, isRuralMode, toggleRuralMode } = useNetworkQuality();
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={toggleRuralMode}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={`px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all duration-300 border cursor-pointer ${
          isRuralMode
            ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.25)]'
            : !isOnline
            ? 'bg-red-500/20 border-red-500/50 text-red-300'
            : 'bg-stone-800/80 border-stone-700/80 text-stone-300 hover:border-amber-500/40 hover:text-white'
        }`}
        aria-label="Toggle Rural 2G Low-Data Mode"
      >
        {!isOnline ? (
          <>
            <WifiOff className="w-3.5 h-3.5 text-red-400 animate-pulse" />
            <span>Offline Cache</span>
          </>
        ) : isRuralMode ? (
          <>
            <SignalLow className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            <span className="hidden sm:inline">Rural 2G Mode</span>
            <span className="sm:hidden">2G</span>
          </>
        ) : (
          <>
            <Signal className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">Network: {effectiveType.toUpperCase()}</span>
            <span className="sm:hidden">{effectiveType.toUpperCase()}</span>
          </>
        )}
      </button>

      {showTooltip && (
        <div className="absolute right-0 top-full mt-2 w-64 p-3 bg-stone-900/95 border border-stone-700/80 rounded-2xl shadow-2xl backdrop-blur-xl z-50 text-xs text-stone-300 pointer-events-none animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-center gap-1.5 font-bold text-white mb-1">
            <ShieldCheck className="w-4 h-4 text-amber-400" />
            <span>Rural Himalayan Mode</span>
          </div>
          <p className="text-[11px] text-stone-400 leading-snug">
            {isRuralMode
              ? 'Active! Optimized for 2G/3G networks in deep forest & mountain border zones. Heavy media & blur effects are disabled.'
              : 'Click to enable Rural 2G Mode for ultra-fast loading on weak signal (2G/3G) in mountain valleys.'}
          </p>
        </div>
      )}
    </div>
  );
}
