'use client';

import React from 'react';
import { CrowdLevel } from '@/types';
import { getCrowdBadgeStyle } from '@/lib/utils';
import { AlertTriangle, CheckCircle2, Flame, Users } from 'lucide-react';

interface CrowdGaugeProps {
  score: number;
  level: CrowdLevel;
  size?: 'sm' | 'md' | 'lg';
  showSubtext?: boolean;
}

export const CrowdGauge: React.FC<CrowdGaugeProps> = ({
  score,
  level,
  size = 'md',
  showSubtext = true
}) => {
  const badge = getCrowdBadgeStyle(level);

  // SVG Gauge calculations
  const strokeWidth = size === 'lg' ? 10 : size === 'md' ? 8 : 6;
  const radius = size === 'lg' ? 76 : size === 'md' ? 58 : 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const dimension = (radius + strokeWidth) * 2;

  let strokeColor = '#059669'; // Emerald
  if (level === 'MEDIUM') strokeColor = '#D97706'; // Warm Amber
  else if (level === 'HIGH') strokeColor = '#EA580C'; // Orange
  else if (level === 'VERY HIGH') strokeColor = '#DC2626'; // Deep Rose/Crimson

  return (
    <div className="flex flex-col items-center text-center">
      <div className="relative flex items-center justify-center">
        <svg
          width={dimension}
          height={dimension}
          className="transform -rotate-90 transition-all duration-1000"
        >
          {/* Background Track */}
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="text-stone-200 dark:text-stone-800/80"
          />
          {/* Active Meter */}
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out drop-shadow-xs"
          />
        </svg>

        {/* Center Score Display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="flex items-baseline">
            <span className="font-extrabold text-3xl sm:text-4xl text-stone-950 dark:text-white tracking-tight font-mono">
              {score}
            </span>
            <span className="text-xs font-semibold text-stone-400 ml-0.5">/100</span>
          </div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-stone-400 mt-0.5">
            Crowd Index
          </span>
        </div>
      </div>

      {/* Classification Tag */}
      <div className="mt-4 flex items-center gap-2">
        <div className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider border flex items-center gap-1.5 ${badge.bg} ${badge.border}`}>
          <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
          <span>{level} FOOTFALL</span>
        </div>
      </div>

      {showSubtext && (
        <p className="text-xs text-stone-500 dark:text-stone-400 mt-2.5 max-w-xs leading-relaxed">
          {level === 'VERY HIGH' && '⚠️ Critical choke points and hotel saturation. We advise immediate diversion.'}
          {level === 'HIGH' && 'Elevated tourist density. Viewpoint queues exceed typical seasonal averages.'}
          {level === 'MEDIUM' && 'Balanced footfall with smooth transit and comfortable lodge availability.'}
          {level === 'LOW' && '✨ Peaceful rural tranquility with minimal ecological footprint.'}
        </p>
      )}
    </div>
  );
};

