'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { 
  AlternativesResponse, 
  DateAlternativesResponse, 
  DestinationDecisionResponse 
} from '@/types';
import { 
  fetchDestinationAlternatives, 
  fetchDateAlternatives, 
  fetchDestinationDecision 
} from '@/lib/api';
import { AlternativeCard } from '@/components/AlternativeCard';
import { getCrowdBadgeStyle, formatINR } from '@/lib/utils';
import { 
  Sparkles, 
  Flame, 
  ArrowLeft, 
  Calendar, 
  MapPin, 
  TrendingDown, 
  ShieldAlert, 
  ShieldCheck, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Compass, 
  Leaf, 
  HelpCircle,
  Split,
  ChevronRight
} from 'lucide-react';

function AlternativesContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = typeof params?.id === 'string' ? params.id : 'darjeeling';

  const [activeTab, setActiveTab] = useState<'DESTINATION' | 'DATES'>('DESTINATION');
  const [altData, setAltData] = useState<AlternativesResponse | null>(null);
  const [dateData, setDateData] = useState<DateAlternativesResponse | null>(null);
  const [decision, setDecision] = useState<DestinationDecisionResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Preferred dates state
  const [prefStartDate, setPrefStartDate] = useState(searchParams.get('start') || '2026-12-25');
  const [prefEndDate, setPrefEndDate] = useState(searchParams.get('end') || '2026-12-27');

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [alts, dates, dec] = await Promise.all([
        fetchDestinationAlternatives(id),
        fetchDateAlternatives(id, prefStartDate, prefEndDate),
        fetchDestinationDecision(id, prefStartDate, prefEndDate)
      ]);
      setAltData(alts);
      setDateData(dates);
      setDecision(dec);
      setLoading(false);
    }
    load();
  }, [id, prefStartDate, prefEndDate]);

  if (loading || !altData || !dateData) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center animate-pulse">
        <div className="h-10 w-64 bg-stone-200 dark:bg-stone-800 rounded-[20px] mx-auto mb-4" />
        <div className="h-6 w-96 bg-stone-200 dark:bg-stone-800 rounded-xl mx-auto" />
      </div>
    );
  }

  const isOvercrowded = altData.origin_crowd_score > 75;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Back Navigation */}
      <div>
        <Link
          href={`/destinations/${id}/crowd`}
          className="inline-flex items-center gap-2 text-xs font-bold text-[#706E68] hover:text-[#171714] dark:hover:text-stone-200 mb-2 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to {altData.origin_destination_name} Crowd Intelligence</span>
        </Link>
      </div>

      {/* Primary Flow Management Hero Banner */}
      <div className={`rounded-[2.5rem] p-8 sm:p-12 text-white shadow-[0_20px_55px_rgba(23,23,20,0.10)] border transition-all ${
        isOvercrowded 
          ? 'bg-stone-950 border-rose-900/40' 
          : 'bg-stone-950 border-stone-800'
      }`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
          <div className="space-y-4 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="px-3.5 py-1 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                <Flame className="w-3.5 h-3.5 animate-pulse" />
                <span>Crowd Pressure: {altData.origin_crowd_score}/100</span>
              </span>
              <span className="px-3 py-1 rounded-full bg-[#FCFAF6]/10 text-[10px] font-bold uppercase tracking-widest text-stone-300">
                SIH 2026 Tourist Flow Engine
              </span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
              {isOvercrowded
                ? `Your destination (${altData.origin_destination_name}) is under critical congestion.`
                : `Active Flow Advisory for ${altData.origin_destination_name}`}
            </h1>

            <p className="text-xs sm:text-sm text-stone-300 leading-relaxed">
              Yatri Setu actively balances tourist distribution to safeguard Himalayan ecosystems. 
              Instead of competing with 91% hotel saturation and gridlocked mountain roads, choose between 
              <strong className="text-white"> shifting to a serene destination</strong> or <strong className="text-white">adjusting your travel dates</strong>.
            </p>
          </div>

          {/* Recommended Flow Action Card */}
          <div className="glass-panel p-6 rounded-[24px] text-center min-w-[280px] self-start lg:self-auto shrink-0 space-y-3">
            <span className="text-[10px] uppercase font-bold tracking-widest text-amber-700 dark:text-amber-400 block">
              Recommended Flow Action
            </span>
            <div className="px-4 py-2.5 rounded-[20px] bg-amber-400 text-[#171714] font-extrabold text-xs tracking-wide shadow-xs">
              {decision?.recommended_action === 'CHANGE_DESTINATION' 
                ? 'A. CHANGE DESTINATION' 
                : decision?.recommended_action === 'CHANGE_DATES'
                ? 'B. CHANGE TRAVEL DATES'
                : 'KEEP DESTINATION'}
            </div>
            <p className="text-xs text-[#706E68] dark:text-stone-300 leading-relaxed">
              {decision?.recommended_action === 'CHANGE_DESTINATION'
                ? 'Divert to Kalimpong (87% Match, 52% lower crowd)'
                : 'Shift to calm mid-week or post-holiday dates'}
            </p>
          </div>
        </div>
      </div>

      {/* Dual Pathway Switcher / Tabs */}
      <div className="flex items-center justify-center p-1.5 bg-stone-200/70 dark:bg-stone-900 rounded-[20px] max-w-lg mx-auto border border-stone-300/80 dark:border-white/10">
        <button
          type="button"
          onClick={() => setActiveTab('DESTINATION')}
          className={`flex-1 py-3 px-5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'DESTINATION'
              ? 'bg-[#FCFAF6] dark:bg-[#121824] text-[#171714] dark:text-white shadow-xs'
              : 'text-[#706E68] dark:text-stone-400 hover:text-[#171714] dark:hover:text-white'
          }`}
        >
          <Compass className="w-4 h-4 text-amber-600" />
          <span>Option A: Change Destination</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('DATES')}
          className={`flex-1 py-3 px-5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'DATES'
              ? 'bg-[#FCFAF6] dark:bg-[#121824] text-[#171714] dark:text-white shadow-xs'
              : 'text-[#706E68] dark:text-stone-400 hover:text-[#171714] dark:hover:text-white'
          }`}
        >
          <Calendar className="w-4 h-4 text-amber-600" />
          <span>Option B: Change Dates</span>
        </button>
      </div>

      {/* ========================================================= */}
      {/* SECTION A: CHANGE DESTINATION (Geographical Decongestion) */}
      {/* ========================================================= */}
      {activeTab === 'DESTINATION' && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
                Pathway A • Geographical Decongestion
              </span>
              <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                Serene Alternate Destinations Near {altData.origin_destination_name}
              </h2>
            </div>
            <span className="text-xs text-slate-500">
              Ranked by similarity & crowd reduction
            </span>
          </div>

          {/* Quick Summary Pill of #1 Recommendation */}
          {altData.alternatives.length > 0 && (
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-[20px] p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#183A32] text-white font-bold flex items-center justify-center shrink-0">
                  #1
                </div>
                <div>
                  <span className="font-extrabold text-slate-900 dark:text-white text-sm">
                    {altData.alternatives[0].name}
                  </span>
                  <span className="text-slate-500 ml-1.5">
                    ({altData.alternatives[0].similarity_score}% Match • {altData.alternatives[0].distance_km} km away • {altData.alternatives[0].crowd_score} Crowd Score)
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-full bg-[#183A32] text-white font-bold text-[10px]">
                  {Math.abs(altData.alternatives[0].cost_difference_percent)}% Cheaper
                </span>
                <Link
                  href={`/itinerary?destination=${altData.alternatives[0].id}`}
                  className="px-3.5 py-1.5 rounded-xl bg-slate-900 text-white dark:bg-[#FCFAF6] dark:text-slate-900 font-bold hover:bg-amber-600 transition-colors"
                >
                  Quick Select →
                </Link>
              </div>
            </div>
          )}

          {/* Alternative Cards */}
          <div className="space-y-6">
            {altData.alternatives.map((alt) => (
              <AlternativeCard
                key={alt.id}
                alternative={alt}
                originName={altData.origin_destination_name}
              />
            ))}
          </div>
        </div>
      )}

      {/* ==================================================== */}
      {/* SECTION B: CHANGE DATES (Temporal Decongestion)      */}
      {/* ==================================================== */}
      {activeTab === 'DATES' && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                Pathway B • Temporal Decongestion
              </span>
              <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                Calmer Seasonal Windows for {altData.origin_destination_name}
              </h2>
            </div>
            <div className="text-xs text-slate-500">
              Current Requested Dates: <strong className="text-slate-800 dark:text-slate-200">{dateData.preferred_start_date} to {dateData.preferred_end_date}</strong> ({dateData.preferred_crowd_score}/100 {dateData.preferred_crowd_classification})
            </div>
          </div>

          {/* Comparative Callout */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-[20px] p-5 text-xs text-amber-900 dark:text-amber-300 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="block text-sm mb-0.5">Stay at {altData.origin_destination_name} with up to 70% lower footfall:</strong>
              By adjusting your departure by just 1 to 2 weeks, you avoid peak holiday bottlenecks, secure up to 42% lower homestay rates, and enjoy unobstructed Kanchenjunga sunrises.
            </div>
          </div>

          {/* 3 Alternative Date Window Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {dateData.date_alternatives.map((dateAlt, idx) => {
              const badge = getCrowdBadgeStyle(dateAlt.crowd_classification);
              return (
                <div
                  key={idx}
                  className="bg-[#FCFAF6] dark:bg-slate-900 rounded-[20px] p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-lg transition-all duration-300 flex flex-col justify-between group"
                >
                  <div>
                    {/* Header with Window Label & Crowd Badge */}
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <span className="text-xs font-extrabold text-amber-600 dark:text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                        Option {idx + 1}
                      </span>
                      <div className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border flex items-center gap-1 ${badge.bg} ${badge.border}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
                        <span>{dateAlt.crowd_score}/100 {dateAlt.crowd_classification}</span>
                      </div>
                    </div>

                    <h3 className="text-xl font-black text-slate-900 dark:text-white tracking-tight">
                      {dateAlt.window_label}
                    </h3>
                    <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                      {dateAlt.start_date} to {dateAlt.end_date}
                    </p>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 gap-2 my-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-center text-xs">
                      <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500/20">
                        <span className="text-[10px] uppercase font-bold text-emerald-600 block">
                          Crowd Reduction
                        </span>
                        <span className="font-black text-emerald-600 text-sm">
                          ↓ {dateAlt.crowd_reduction_percent}% Lower
                        </span>
                      </div>

                      <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block">
                          Tariff Savings
                        </span>
                        <span className="font-black text-slate-900 dark:text-white text-sm">
                          {dateAlt.estimated_cost_change}
                        </span>
                      </div>
                    </div>

                    {/* Availability Score */}
                    <div className="mb-3 flex items-center justify-between text-xs text-slate-500">
                      <span>Room Availability:</span>
                      <strong className="text-emerald-600 dark:text-emerald-400">{dateAlt.availability_score}% Open</strong>
                    </div>

                    {/* Structured Reason */}
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-xl">
                      {dateAlt.reason}
                    </p>
                  </div>

                  {/* CTA */}
                  <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
                    <Link
                      href={`/itinerary?destination=${altData.origin_destination_id}&start=${dateAlt.start_date}&end=${dateAlt.end_date}`}
                      className="w-full py-2.5 rounded-xl bg-slate-900 dark:bg-[#FCFAF6] text-white dark:text-slate-900 hover:bg-amber-600 dark:hover:bg-amber-500 dark:hover:text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-95"
                    >
                      <Calendar className="w-3.5 h-3.5" />
                      <span>Choose These Dates & Plan</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AlternativesPage() {
  return (
    <Suspense fallback={
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading flow management advisor...
      </div>
    }>
      <AlternativesContent />
    </Suspense>
  );
}
