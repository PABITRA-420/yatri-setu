import React from 'react';
import { CrowdFactorItem } from '@/types';
import { HelpCircle, BarChart3, Info } from 'lucide-react';

interface CrowdFactorBreakdownProps {
  factors: CrowdFactorItem[];
  crowdScore: number;
}

export const CrowdFactorBreakdown: React.FC<CrowdFactorBreakdownProps> = ({ factors, crowdScore }) => {
  return (
    <div className="bg-white dark:bg-[#121824] rounded-3xl p-6 sm:p-8 border border-stone-200/80 dark:border-white/10 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-stone-100 dark:border-white/5">
        <div className="flex items-center gap-2.5">
          <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-700 dark:text-amber-400">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-base text-stone-950 dark:text-white tracking-tight">
              Deterministic Multi-Factor Scoring
            </h3>
            <p className="text-xs text-stone-500">
              Formula: 35% Historical + 25% Booking + 15% Season + 10% Holiday + 10% Weather + 5% Road Choke
            </p>
          </div>
        </div>

        <span className="text-[11px] font-bold tracking-wider uppercase px-3 py-1 rounded-full bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 self-start sm:self-auto border border-stone-200/60 dark:border-white/5">
          SIH Deterministic Model
        </span>
      </div>

      <div className="space-y-5">
        {factors.map((factor) => {
          let barColor = 'bg-emerald-600';
          if (factor.raw_value > 75) barColor = 'bg-rose-600';
          else if (factor.raw_value > 50) barColor = 'bg-amber-600';
          else if (factor.raw_value > 25) barColor = 'bg-amber-500';

          return (
            <div key={factor.key} className="group">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-stone-900 dark:text-stone-200">
                    {factor.name}
                  </span>
                  <span className="text-[10px] font-bold text-stone-400 bg-stone-100 dark:bg-stone-800 px-2 py-0.5 rounded-md">
                    Weight: {factor.weight_percentage}%
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-stone-400 font-mono text-xs">
                    Raw: {factor.raw_value}/100
                  </span>
                  <span className="font-extrabold text-stone-950 dark:text-white font-mono text-xs">
                    +{factor.weighted_contribution.toFixed(1)} pts
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 rounded-full bg-stone-100 dark:bg-stone-800/80 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ease-out ${barColor}`}
                  style={{ width: `${factor.raw_value}%` }}
                />
              </div>

              <p className="text-[11px] text-stone-500 dark:text-stone-400 mt-1 leading-relaxed">
                {factor.description}
              </p>
            </div>
          );
        })}
      </div>

      <div className="mt-8 pt-5 border-t border-stone-100 dark:border-white/5 flex items-center justify-between text-xs text-stone-500">
        <div className="flex items-center gap-1.5">
          <Info className="w-4 h-4 text-amber-600" />
          <span>Sum of weighted contributions matches aggregate crowd index:</span>
        </div>
        <span className="font-mono font-extrabold text-base text-stone-950 dark:text-white">
          {crowdScore} / 100
        </span>
      </div>
    </div>
  );
};

