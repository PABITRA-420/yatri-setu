'use client';

import React, { useState } from 'react';
import { ItineraryDay, ActivitySlot } from '@/types';
import { formatINR } from '@/lib/utils';
import { motion } from 'motion/react';
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
      <div className="p-8 text-center text-stone-500">
        No itinerary days available.
      </div>
    );
  }

  const currentDay = days[activeDayIdx];

  const getPeriodIcon = (period: string) => {
    switch (period) {
      case 'Morning':
        return <Sun className="w-4 h-4 text-amber-400" />;
      case 'Afternoon':
        return <Sunset className="w-4 h-4 text-orange-400" />;
      case 'Evening':
        return <Moon className="w-4 h-4 text-indigo-400" />;
      default:
        return <Clock className="w-4 h-4 text-stone-400" />;
    }
  };

  return (
    <div className="bg-stone-900/80 backdrop-blur-xl rounded-3xl border border-white/10 p-6 sm:p-8 shadow-xl">
      {/* Day Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-4 border-b border-white/10 scrollbar-none">
        {days.map((day, idx) => (
          <button
            key={day.day_number}
            onClick={() => setActiveDayIdx(idx)}
            className={`px-4 py-2.5 rounded-2xl text-xs font-bold transition-all whitespace-nowrap flex items-center gap-2 active:scale-95 ${
              activeDayIdx === idx
                ? 'bg-amber-400 text-stone-950 font-black shadow-lg shadow-amber-500/20 scale-102'
                : 'bg-stone-950/60 text-stone-300 border border-white/5 hover:bg-white/10'
            }`}
          >
            <span>Day {day.day_number}</span>
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${activeDayIdx === idx ? 'bg-stone-950 text-amber-300 font-mono' : 'bg-stone-800 text-stone-400 font-mono'}`}>
              {formatINR(day.estimated_budget_inr * personMultiplier)}
            </span>
          </button>
        ))}
      </div>

      {/* Active Day Header */}
      <div className="py-5 border-b border-white/10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-[10px] uppercase font-bold text-amber-400 tracking-wider block">
              Day {currentDay.day_number} Himalayan Focus
            </span>
            <h3 className="text-xl font-extrabold text-white mt-0.5 tracking-tight">
              {currentDay.theme}
            </h3>
          </div>
          <div className="flex items-center gap-2 text-xs text-stone-300 bg-stone-950/80 px-3.5 py-2 rounded-2xl border border-white/10">
            <Bus className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Transit: {currentDay.transit_advice}</span>
          </div>
        </div>
        <p className="text-xs text-stone-400 mt-2 leading-relaxed">
          {currentDay.overview}
        </p>
      </div>

      {/* Activity Timeline List */}
      <div className="relative mt-8 space-y-6 before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-gradient-to-b before:from-amber-500 before:via-emerald-500 before:to-stone-800">
        {currentDay.activities.map((activity, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.08 }}
            className="relative flex items-start gap-4 group"
          >
            {/* Timeline Marker */}
            <div className="relative z-10 w-7 h-7 rounded-full bg-stone-950 border-2 border-amber-400 text-white flex items-center justify-center shadow-lg shadow-amber-500/20 shrink-0 group-hover:scale-110 transition-transform">
              {getPeriodIcon(activity.period)}
            </div>

            {/* Content Card */}
            <div className="flex-1 bg-stone-950/70 hover:bg-stone-950/90 border border-white/10 hover:border-amber-500/30 rounded-2xl p-5 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-amber-400 flex items-center gap-1 font-mono">
                    <Clock className="w-3.5 h-3.5" />
                    {activity.time_slot}
                  </span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-white/10 text-stone-300">
                    {activity.category}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                    Crowd: {activity.crowd_forecast}
                  </span>
                  <span className="font-bold text-white font-mono">
                    {activity.cost_estimate_inr === 0 ? 'Free Entry' : formatINR(activity.cost_estimate_inr)}
                  </span>
                </div>
              </div>

              <h4 className="font-extrabold text-base text-white tracking-tight">
                {activity.title}
              </h4>
              <p className="text-xs text-stone-400 mt-1 leading-relaxed">
                {activity.description}
              </p>

              {activity.is_weather_adapted && (
                <div className="mt-3 px-3.5 py-2 rounded-xl bg-blue-500/15 border border-blue-500/30 text-blue-200 text-xs flex items-center gap-2">
                  <span className="shrink-0 text-sm">🌧️</span>
                  <div>
                    <span className="font-bold">Weather Adaptive Substitution: </span>
                    <span>{activity.adaptation_reason || 'Yatri Setu adapted this activity because of expected mountain rain.'}</span>
                  </div>
                </div>
              )}

              <div className="mt-4 flex flex-wrap items-center gap-4 pt-3 border-t border-white/5 text-[11px] text-stone-400">
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-amber-400" />
                  <span>{activity.location_name}</span>
                </div>
                {activity.travel_tip && (
                  <div className="flex items-center gap-1.5 text-amber-300">
                    <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
                    <span>Tip: {activity.travel_tip}</span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

    </div>
  );
};
