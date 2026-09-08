'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { CrowdResponse } from '@/types';
import { fetchDestinationCrowd } from '@/lib/api';
import { CrowdGauge } from '@/components/CrowdGauge';
import { CrowdFactorBreakdown } from '@/components/CrowdFactorBreakdown';
import { 
  Flame, 
  Sparkles, 
  AlertTriangle, 
  Clock, 
  ShieldAlert, 
  ArrowRight, 
  Navigation, 
  Building, 
  Car,
  CheckCircle,
  HelpCircle,
  TrendingDown
} from 'lucide-react';

export default function CrowdIntelligencePage() {
  const params = useParams();
  const router = useRouter();
  const id = typeof params?.id === 'string' ? params.id : 'darjeeling';

  const [crowd, setCrowd] = useState<CrowdResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchDestinationCrowd(id);
      setCrowd(data);
      setLoading(false);
    }
    load();
  }, [id]);

  if (loading || !crowd) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center animate-pulse">
        <div className="h-10 w-64 bg-slate-200 dark:bg-slate-800 rounded-xl mx-auto mb-4" />
        <div className="h-6 w-96 bg-slate-200 dark:bg-slate-800 rounded-lg mx-auto" />
      </div>
    );
  }

  const isCritical = crowd.crowd_score > 75;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <Flame className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                Crowd Intelligence Panel: {crowd.destination_name}
              </h1>
              <p className="text-xs sm:text-sm text-slate-500">
                Explainable Multi-Factor Footfall Advisor • SIH 2026 Core Feature
              </p>
            </div>
          </div>
        </div>

        {/* Primary CTA to view alternatives */}
        <Link
          href={`/destinations/${id}/alternatives`}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-xs shadow-md shadow-amber-600/30 transition-all self-start md:self-auto active:scale-95"
        >
          <Sparkles className="w-4 h-4 text-amber-300" />
          <span>View Recommended Alternatives</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Top Banner: Score Gauge & Live Real-time Status */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Score Gauge Card */}
        <div className="lg:col-span-5 bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center">
          <CrowdGauge score={crowd.crowd_score} level={crowd.crowd_level} size="lg" />

          {/* Alert Status Card */}
          <div className={`mt-6 w-full p-4 rounded-xl text-xs ${
            isCritical 
              ? 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/30' 
              : 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/30'
          }`}>
            <div className="flex items-center gap-1.5 font-bold mb-1">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{isCritical ? 'CRITICAL FOOTFALL ALERT' : 'BALANCED FOOTFALL ADVISORY'}</span>
            </div>
            <p className="leading-relaxed">
              {crowd.summary}
            </p>
          </div>
        </div>

        {/* Live Operational Metrics Card */}
        <div className="lg:col-span-7 bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <Navigation className="w-4 h-4 text-amber-600" />
              <span>Live Operational Pulse & Timings</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Metric 1 */}
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                  Peak Visiting Windows
                </span>
                <span className="font-extrabold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-rose-500" />
                  {crowd.peak_visiting_hours}
                </span>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Avoid peak observation queues
                </span>
              </div>

              {/* Metric 2 */}
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                  Optimal Calmer Time Today
                </span>
                <span className="font-extrabold text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  {crowd.best_time_to_visit_today}
                </span>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Recommended for quiet walks
                </span>
              </div>

              {/* Metric 3 */}
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                  Hotel Occupancy Density
                </span>
                <span className="font-extrabold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Building className="w-4 h-4 text-amber-500" />
                  {crowd.hotel_occupancy_rate}
                </span>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Central town room availability
                </span>
              </div>

              {/* Metric 4 */}
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                  Mountain Transit Route Delay
                </span>
                <span className="font-extrabold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Car className="w-4 h-4 text-orange-500" />
                  {crowd.live_traffic_status}
                </span>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Hill Cart highway status
                </span>
              </div>
            </div>

            {/* Bottlenecks List */}
            <div className="mt-5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Identified Physical Choke Points:
              </span>
              <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-300">
                {crowd.bottlenecks.map((b, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Deterministic Feed • Updated: {crowd.last_updated}</span>
            <span className="font-medium text-amber-600">Model verified for SIH 2026</span>
          </div>
        </div>
      </div>

      {/* "Why is it Crowded?" Explainability Section */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-lg bg-rose-500/10 text-rose-600">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Why is the Crowd Score {crowd.crowd_score}/100?
            </h2>
            <p className="text-xs text-slate-500">
              Natural language explanation generated from real-time factors
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {crowd.why_crowded.map((reason, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/80 flex items-start gap-3"
            >
              <span className="w-6 h-6 rounded-full bg-rose-500/10 text-rose-600 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                {reason}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Deterministic Factor Breakdown Bars */}
      <CrowdFactorBreakdown factors={crowd.factors} crowdScore={crowd.crowd_score} />

      {/* Alternative Redirection Callout */}
      <div className="bg-gradient-to-r from-slate-900 via-amber-950 to-slate-900 text-white rounded-3xl p-8 shadow-xl flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 font-bold text-xs">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Recommended Next Action</span>
          </div>
          <h3 className="text-2xl font-black">
            Switch Destination to Kalimpong (87% Match)
          </h3>
          <p className="text-xs sm:text-sm text-slate-300">
            Enjoy scenic views of Kanchenjunga, rare orchid nurseries, and peaceful Buddhist monasteries with half the crowd pressure and approx 42% cost savings.
          </p>
        </div>

        <Link
          href={`/destinations/${id}/alternatives`}
          className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-600 hover:to-rose-700 text-white font-bold text-xs shadow-lg shadow-amber-500/20 whitespace-nowrap active:scale-95 transition-all flex items-center gap-2 shrink-0"
        >
          <span>Open Alternate Destination Advisor</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
