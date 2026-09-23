'use client';

import React from 'react';

interface SkeletonCardProps {
  index?: number;
  className?: string;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({ index = 0, className = '' }) => {
  const delay = `${index * 120}ms`;

  return (
    <div
      className={`neo-card relative flex flex-col justify-between rounded-3xl bg-white dark:bg-[#121824] border border-stone-200/80 dark:border-white/10 overflow-hidden ${className}`}
    >
      <div>
        {/* Shimmering Cover Image Area */}
        <div className="relative h-60 sm:h-64 w-full overflow-hidden bg-stone-200 dark:bg-stone-800/70">
          <div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 dark:via-white/10 to-transparent animate-shimmer"
            style={{ animationDelay: delay }}
          />

          {/* Top-Right Badge Placeholder */}
          <div className="absolute top-3.5 right-3.5">
            <div className="h-6 w-24 rounded-full bg-stone-300/80 dark:bg-stone-700/60 backdrop-blur-sm" />
          </div>

          {/* Bottom-Left Region Placeholder */}
          <div className="absolute bottom-3.5 left-4 flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-stone-300/80 dark:bg-stone-700/60" />
            <div className="h-3.5 w-28 rounded bg-stone-300/80 dark:bg-stone-700/60" />
          </div>
        </div>

        {/* Content Section */}
        <div className="p-6 space-y-4">
          {/* Title */}
          <div className="relative overflow-hidden">
            <div className="h-6 w-3/4 rounded-xl bg-stone-200 dark:bg-stone-800" />
            <div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 dark:via-white/10 to-transparent animate-shimmer"
              style={{ animationDelay: delay }}
            />
          </div>

          {/* Tagline / Description Lines */}
          <div className="space-y-2 relative overflow-hidden">
            <div className="h-3.5 w-full rounded bg-stone-200 dark:bg-stone-800/80" />
            <div className="h-3.5 w-4/5 rounded bg-stone-200 dark:bg-stone-800/80" />
            <div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 dark:via-white/10 to-transparent animate-shimmer"
              style={{ animationDelay: delay }}
            />
          </div>

          {/* Chips */}
          <div className="flex flex-wrap gap-2 pt-1">
            <div className="h-6 w-16 rounded-md bg-stone-200 dark:bg-stone-800/70" />
            <div className="h-6 w-20 rounded-md bg-stone-200 dark:bg-stone-800/70" />
            <div className="h-6 w-14 rounded-md bg-stone-200 dark:bg-stone-800/70" />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 pb-6 pt-3 border-t border-stone-100 dark:border-white/5 flex items-center justify-between">
        <div className="space-y-1">
          <div className="h-2.5 w-16 rounded bg-stone-200 dark:bg-stone-800/80" />
          <div className="h-5 w-20 rounded bg-stone-200 dark:bg-stone-800" />
        </div>

        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-stone-200 dark:bg-stone-800" />
          <div className="h-9 w-20 rounded-xl bg-stone-200 dark:bg-stone-800" />
        </div>
      </div>
    </div>
  );
};

export const FetchProgressBar: React.FC<{ loading: boolean }> = ({ loading }) => {
  if (!loading) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-1 bg-transparent overflow-hidden">
      <div className="h-full bg-gradient-to-r from-amber-500 via-rose-500 to-amber-500 w-full animate-shimmer" />
    </div>
  );
};
