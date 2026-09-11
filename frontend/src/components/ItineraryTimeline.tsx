'use client';

import React, { useState } from 'react';
import { ItineraryDay, ActivitySlot } from '@/types';
import { formatINR } from '@/lib/utils';
import { 
  Clock, 
  MapPin, 
  Lightbulb, 
  Bus, 
  Sun, 
  Sunset, 
  Moon,
  Sparkles,
  CheckCircle2
} from 'lucide-react';

interface ItineraryTimelineProps {
  days: ItineraryDay[];
  personMultiplier?: number;
}

export const ItineraryTimeline: React.FC<ItineraryTimelineProps> = ({ days, personMultiplier = 1 }) => {
  const [activeDayIdx, setActiveDayIdx] = useState(0);

  if (!days || days.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500">
        No itinerary days available.
      </div>
    );
  }

  const currentDay = days[activeDayIdx];

  const getPeriodIcon = (period: string) => {
    switch (period) {
      case 'Morning':
        return <Sun className="w-4 h-4 text-amber-500" />;
      case 'Afternoon':
        return <Sunset className="w-4 h-4 text-orange-500" />;
      case 'Evening':
        return <Moon className="w-4 h-4 text-indigo-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm">
      {/* Day Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-3 border-b border-slate-100 dark:border-slate-800 scrollbar-none">
        {days.map((day, idx) => (
          <button
            key={day.day_number}
            onClick={() => setActiveDayIdx(idx)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap flex items-center gap-2 ${
              activeDayIdx === idx
                ? 'bg-amber-600 text-white shadow-md shadow-amber-600/20 scale-102'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            <span>Day {day.day_number}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${activeDayIdx === idx ? 'bg-amber-700/80 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-500'}`}>
              {formatINR(day.estimated_budget_inr * personMultiplier)}
            </span>
          </button>
        ))}
      </div>

      {/* Active Day Header */}
      <div className="py-4 border-b border-slate-100 dark:border-slate-800/80">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <span className="text-[10px] uppercase font-bold text-amber-600 dark:text-amber-400 tracking-wider">
              Day {currentDay.day_number} Focus
            </span>
            <h3 className="text-lg font-black text-slate-900 dark:text-white">
              {currentDay.theme}
            </h3>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-500 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200/60 dark:border-slate-700/60">
            <Bus className="w-3.5 h-3.5 text-amber-500" />
            <span>Transit: {currentDay.transit_advice}</span>
          </div>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-300 mt-2">
          {currentDay.overview}
        </p>
      </div>

      {/* Activity Timeline List */}
      <div className="relative mt-6 space-y-6 before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
        {currentDay.activities.map((activity, idx) => (
          <div key={idx} className="relative flex items-start gap-4 group">
            {/* Timeline Marker */}
            <div className="relative z-10 w-7 h-7 rounded-full bg-amber-500 text-white flex items-center justify-center shadow-md shadow-amber-500/30 shrink-0 group-hover:scale-110 transition-transform">
              {getPeriodIcon(activity.period)}
            </div>

            {/* Content Card */}
            <div className="flex-1 bg-slate-50/70 dark:bg-slate-800/50 hover:bg-slate-100/70 dark:hover:bg-slate-800 border border-slate-200/70 dark:border-slate-700/70 rounded-xl p-4 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-amber-600 dark:text-amber-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {activity.time_slot}
                  </span>
                  <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-md bg-slate-200/80 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                    {activity.category}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    Crowd: {activity.crowd_forecast}
                  </span>
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    {activity.cost_estimate_inr === 0 ? 'Free Entry' : formatINR(activity.cost_estimate_inr)}
                  </span>
                </div>
              </div>

              <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                {activity.title}
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-1">
                {activity.description}
              </p>

              {activity.is_weather_adapted && (
                <div className="mt-2.5 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-700 dark:text-blue-300 text-[11px] flex items-center gap-2">
                  <span className="shrink-0 text-sm">🌧️</span>
                  <div>
                    <span className="font-bold">Weather Adaptive Substitution: </span>
                    <span>{activity.adaptation_reason || 'Yatri Setu adapted this activity because of expected mountain rain.'}</span>
                  </div>
                </div>
              )}

              <div className="mt-3 flex flex-wrap items-center gap-3 pt-2 border-t border-slate-200/50 dark:border-slate-700/50 text-[11px] text-slate-500">
                <div className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-400" />
                  <span>{activity.location_name}</span>
                </div>
                {activity.travel_tip && (
                  <div className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                    <Lightbulb className="w-3 h-3" />
                    <span>Tip: {activity.travel_tip}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
