import React from 'react';
import { CrowdFactorItem } from '@/types';
import { HelpCircle, BarChart3, Info } from 'lucide-react';

interface CrowdFactorBreakdownProps {
  factors: CrowdFactorItem[];
  crowdScore: number;
}

export const CrowdFactorBreakdown: React.FC<CrowdFactorBreakdownProps> = ({ factors, crowdScore }) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white">
              Deterministic Multi-Factor Scoring
            </h3>
            <p className="text-xs text-slate-500">
              Formula: 35% Historical + 25% Booking + 15% Season + 10% Holiday + 10% Weather + 5% Traffic
            </p>
          </div>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
          Rule-Based Model
        </span>
      </div>

      <div className="space-y-4">
        {factors.map((factor) => {
          let barColor = 'bg-emerald-500';
          if (factor.raw_value > 75) barColor = 'bg-rose-500';
          else if (factor.raw_value > 50) barColor = 'bg-orange-500';
          else if (factor.raw_value > 25) barColor = 'bg-amber-500';

          return (
            <div key={factor.key} className="group">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <div className="flex items-center gap-1.5">
                  <span className="font-semibold text-slate-800 dark:text-slate-200">
                    {factor.name}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">
                    Weight: {factor.weight_percentage}%
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                    Raw: {factor.raw_value}/100
                  </span>
                  <span className="font-bold text-slate-900 dark:text-white font-mono text-[11px]">
                    +{factor.weighted_contribution.toFixed(1)} pts
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ease-out ${barColor}`}
                  style={{ width: `${factor.raw_value}%` }}
                />
              </div>

              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                {factor.description}
              </p>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-1.5">
          <Info className="w-4 h-4 text-amber-500" />
          <span>Sum of weighted contributions matches total index:</span>
        </div>
        <span className="font-mono font-bold text-slate-900 dark:text-white">
          {crowdScore} / 100
        </span>
      </div>
    </div>
  );
};
