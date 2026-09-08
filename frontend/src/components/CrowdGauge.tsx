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
  const strokeWidth = size === 'lg' ? 12 : size === 'md' ? 10 : 8;
  const radius = size === 'lg' ? 70 : size === 'md' ? 55 : 40;
  const circumference = 2 * Math.PI * radius;
  // Use a 270 degree arc for gauge look
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const dimension = (radius + strokeWidth) * 2;

  let strokeColor = '#10B981'; // LOW
  if (level === 'MEDIUM') strokeColor = '#F59E0B';
  else if (level === 'HIGH') strokeColor = '#F97316';
  else if (level === 'VERY HIGH') strokeColor = '#E11D48';

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
            className="text-slate-100 dark:text-slate-800"
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
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Score Display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="flex items-baseline">
            <span className="font-black text-3xl sm:text-4xl text-slate-900 dark:text-white tracking-tight">
              {score}
            </span>
            <span className="text-xs font-semibold text-slate-400 ml-0.5">/100</span>
          </div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Crowd Index
          </span>
        </div>
      </div>

      {/* Classification Tag */}
      <div className="mt-3 flex items-center gap-2">
        <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border flex items-center gap-1.5 ${badge.bg} ${badge.border}`}>
          <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
          <span>{level} CROWD</span>
        </div>
      </div>

      {showSubtext && (
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 max-w-xs">
          {level === 'VERY HIGH' && '⚠️ Severe bottlenecks and critical hotel saturation. Consider nearby alternatives.'}
          {level === 'HIGH' && 'High tourist concentration. Expect queues at viewpoints.'}
          {level === 'MEDIUM' && 'Balanced visitor flow with smooth mountain connectivity.'}
          {level === 'LOW' && '✨ Peaceful rural tranquility with minimal ecological footfall.'}
        </p>
      )}
    </div>
  );
};
