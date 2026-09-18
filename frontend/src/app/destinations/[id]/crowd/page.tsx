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
  TrendingDown,
  Compass
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
      <div className="max-w-7xl mx-auto px-4 py-24 text-center animate-pulse">
        <div className="h-10 w-64 bg-stone-200 dark:bg-stone-800 rounded-2xl mx-auto mb-4" />
        <div className="h-6 w-96 bg-stone-200 dark:bg-stone-800 rounded-xl mx-auto" />
      </div>
    );
  }

  const isCritical = crowd.crowd_score > 75;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Hero Header with Blurred Background Image */}
      <div className="relative rounded-3xl overflow-hidden shadow-2xl border border-stone-200 dark:border-white/10">
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <img 
            src="/image2.png" 
            alt="Forest backdrop" 
            className="w-full h-full object-cover blur-[3px] scale-105 brightness-[0.7] dark:brightness-[0.4]"
          />
          {/* Gradient Overlay for text legibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-stone-950/90 via-stone-900/50 to-stone-900/30"></div>
        </div>

        {/* Header Content */}
        <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-6 p-8 sm:p-12">
          <div>
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-md text-amber-400 shadow-inner border border-white/20">
                <Flame className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-amber-400 drop-shadow-md">
                    SIH 2026 Core Innovation
                  </span>
                </div>
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight drop-shadow-lg">
                  Crowd Intelligence: <br className="hidden sm:block" />{crowd.destination_name}
                </h1>
                <p className="text-xs sm:text-sm text-stone-200 mt-3 font-medium drop-shadow-md max-w-xl">
                  Deterministic Multi-Factor Footfall Advisor & Capacity Management
                </p>
              </div>
            </div>
          </div>

          {/* Primary CTA to view alternatives */}
          <Link
            href={`/destinations/${id}/alternatives`}
            className="flex items-center gap-2 px-6 py-4 rounded-2xl bg-amber-500 hover:bg-amber-400 text-stone-950 font-extrabold text-xs shadow-[0_0_30px_rgba(245,158,11,0.4)] transition-all self-start md:self-auto active:scale-95"
          >
            <Sparkles className="w-4 h-4" />
            <span>View Suggested Alternatives</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Top Banner: Score Gauge & Live Real-time Status */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Score Gauge Card */}
        <div className="lg:col-span-5 bg-white dark:bg-[#121824] rounded-3xl p-8 border border-stone-200/80 dark:border-white/10 shadow-xs flex flex-col items-center justify-center">
          <CrowdGauge score={crowd.crowd_score} level={crowd.crowd_level} size="lg" />

          {/* Alert Status Card */}
          <div className={`mt-7 w-full p-5 rounded-2xl text-xs leading-relaxed ${
            isCritical 
              ? 'bg-rose-50 text-rose-800 dark:bg-rose-950/30 dark:text-rose-300 border border-rose-200 dark:border-rose-900/60' 
              : 'bg-amber-50 text-amber-800 dark:bg-amber-950/30 dark:text-amber-300 border border-amber-200 dark:border-amber-900/60'
          }`}>
            <div className="flex items-center gap-2 font-bold mb-1.5 uppercase tracking-wider text-[11px]">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{isCritical ? 'CRITICAL FOOTFALL ADVISORY' : 'BALANCED FOOTFALL ADVISORY'}</span>
            </div>
            <p>
              {crowd.summary}
            </p>
          </div>
        </div>

        {/* Live Operational Metrics Card */}
        <div className="lg:col-span-7 bg-white dark:bg-[#121824] rounded-3xl p-8 border border-stone-200/80 dark:border-white/10 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-base text-stone-950 dark:text-white mb-5 flex items-center gap-2 tracking-tight">
              <Navigation className="w-4 h-4 text-amber-600" />
              <span>Live Operational Pulse & Timings</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Metric 1 */}
              <div className="p-4 rounded-2xl bg-stone-50 dark:bg-stone-900/60 border border-stone-200/60 dark:border-white/5">
                <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block mb-1">
                  Peak Visiting Windows
                </span>
                <span className="font-extrabold text-sm text-stone-950 dark:text-white flex items-center gap-1.5 font-mono">
                  <Clock className="w-4 h-4 text-rose-600" />
                  {crowd.peak_visiting_hours}
                </span>
                <span className="text-[11px] text-stone-500 mt-1 block">
                  Avoid observation deck queues
                </span>
              </div>

              {/* Metric 2 */}
              <div className="p-4 rounded-2xl bg-stone-50 dark:bg-stone-900/60 border border-stone-200/60 dark:border-white/5">
                <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block mb-1">
                  Optimal Calmer Window Today
                </span>
                <span className="font-extrabold text-sm text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5 font-mono">
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  {crowd.best_time_to_visit_today}
                </span>
                <span className="text-[11px] text-stone-500 mt-1 block">
                  Ideal for quiet nature walks
                </span>
              </div>

              {/* Metric 3 */}
              <div className="p-4 rounded-2xl bg-stone-50 dark:bg-stone-900/60 border border-stone-200/60 dark:border-white/5">
                <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block mb-1">
                  Hotel Occupancy Density
                </span>
                <span className="font-extrabold text-sm text-stone-950 dark:text-white flex items-center gap-1.5 font-mono">
                  <Building className="w-4 h-4 text-amber-600" />
                  {crowd.hotel_occupancy_rate}
                </span>
                <span className="text-[11px] text-stone-500 mt-1 block">
                  Town center room availability
                </span>
              </div>

              {/* Metric 4 */}
              <div className="p-4 rounded-2xl bg-stone-50 dark:bg-stone-900/60 border border-stone-200/60 dark:border-white/5">
                <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block mb-1">
                  Choke Point Road Traffic
                </span>
                <span className="font-extrabold text-sm text-stone-950 dark:text-white flex items-center gap-1.5 font-mono">
                  <Car className="w-4 h-4 text-amber-600" />
                  {crowd.live_traffic_status}
                </span>
                <span className="text-[11px] text-stone-500 mt-1 block">
                  Hill Cart Road & Ghoom Junction
                </span>
              </div>
            </div>

            {/* Bottlenecks List */}
            <div className="mt-5">
              <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-2">
                Identified Physical Choke Points:
              </span>
              <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-300">
                {(Array.isArray(crowd.bottlenecks) ? crowd.bottlenecks : []).map((b, i) => (
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
      <div className="bg-white dark:bg-[#121824] rounded-3xl p-7 sm:p-8 border border-stone-200/80 dark:border-white/10 shadow-xs">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2.5 rounded-2xl bg-rose-500/10 text-rose-700 dark:text-rose-400">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-stone-950 dark:text-white tracking-tight">
              Why is the Crowd Score {crowd.crowd_score}/100?
            </h2>
            <p className="text-xs text-stone-500">
              Natural language explanation synthesized from deterministic factors
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(Array.isArray(crowd.why_crowded) ? crowd.why_crowded : []).map((reason, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-stone-50 dark:bg-stone-900/60 border border-stone-200/60 dark:border-white/5 flex items-start gap-3.5"
            >
              <span className="w-6 h-6 rounded-full bg-rose-500/10 text-rose-700 dark:text-rose-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5 font-mono">
                {idx + 1}
              </span>
              <p className="text-xs sm:text-sm text-stone-700 dark:text-stone-300 leading-relaxed">
                {reason}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Deterministic Factor Breakdown Bars */}
      <CrowdFactorBreakdown factors={crowd.factors} crowdScore={crowd.crowd_score} />

      {/* Alternative Redirection Callout */}
      <div className="bg-stone-950 text-white rounded-[2.5rem] p-8 sm:p-12 shadow-2xl border border-stone-800 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-3 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-amber-400/20 text-amber-300 font-bold text-xs uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Suggested Next Action</span>
          </div>
          <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Switch Destination to Kalimpong (87% Match)
          </h3>
          <p className="text-xs sm:text-sm text-stone-300 leading-relaxed">
            Enjoy panoramic views of Kanchenjunga, rare orchid nurseries, and peaceful Buddhist monasteries with half the crowd pressure and approx 42% cost savings.
          </p>
        </div>

        <Link
          href={`/destinations/${id}/alternatives`}
          className="px-6 py-3.5 rounded-2xl bg-amber-400 hover:bg-amber-300 text-stone-950 font-bold text-xs shadow-lg active:scale-97 transition-all flex items-center gap-2 whitespace-nowrap"
        >
          <span>Compare Kalimpong & Stays</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
