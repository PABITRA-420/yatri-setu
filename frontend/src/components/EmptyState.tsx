'use client';

import React from 'react';
import { Compass, RefreshCw } from 'lucide-react';

interface EmptyStateProps {
  message?: string;
  onReset?: () => void;
}

export function EmptyState({ message = 'No items match your selected filters.', onReset }: EmptyStateProps) {
  return (
    <div className="text-center py-16 px-6 bg-stone-900/60 backdrop-blur-xl rounded-3xl border border-white/10 shadow-xl max-w-md mx-auto my-6 space-y-4">
      <div className="w-16 h-16 rounded-3xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mx-auto shadow-inner">
        <Compass className="w-8 h-8 animate-pulse" />
      </div>

      <h3 className="font-extrabold text-base text-white tracking-tight">No Results Found</h3>

      <p className="text-xs text-stone-400 leading-relaxed max-w-xs mx-auto">
        {message}
      </p>

      {onReset && (
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-stone-950 font-extrabold text-xs transition-all active:scale-95 shadow-lg shadow-amber-500/20"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Filter Controls</span>
        </button>
      )}
    </div>
  );
}
