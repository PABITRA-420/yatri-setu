'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  TrendingUp, 
  ArrowLeft, 
  Users, 
  MapPin, 
  HeartHandshake, 
  Award, 
  Sparkles, 
  Landmark,
  ArrowUpRight,
  ChevronRight
} from 'lucide-react';
import { fetchPanchayatAnalytics, fetchDestinationFlowImpact } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { DestinationFlowImpact } from '@/types';

export default function PanchayatAnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [darjImpact, setDarjImpact] = useState<DestinationFlowImpact | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [ana, imp] = await Promise.all([
          fetchPanchayatAnalytics(),
          fetchDestinationFlowImpact('darjeeling')
        ]);
        setAnalytics(ana);
        setDarjImpact(imp);
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <Link href="/panchayat" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-emerald-600 transition-colors mb-2">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Panchayat Desk</span>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-3">
            <TrendingUp className="w-7 h-7 text-emerald-600" />
            <span>Rural Economic Impact Analytics</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            Tourism flow redistribution results — Darjeeling pressure relief & village income generation
          </p>
        </div>

        {loading || !analytics || !darjImpact ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-emerald-600 mx-auto" />
          </div>
        ) : (
          <>
            {/* Crowd Diversion Hero Stat Block */}
            <div className="bg-gradient-to-br from-slate-900 via-emerald-950 to-slate-900 text-white rounded-3xl p-6 sm:p-8 border border-emerald-500/20 shadow-xl">
              <div className="flex items-center gap-2 mb-6">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold uppercase tracking-widest text-emerald-300">
                  Yatri Setu Mission Impact — Darjeeling Crowd Relief
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                <div className="text-center space-y-1">
                  <div className="text-3xl font-black text-amber-400">
                    {analytics.summary.total_redirected_tourists.toLocaleString()}
                  </div>
                  <div className="text-xs text-slate-300">Travelers Redirected from Darjeeling</div>
                </div>
                <div className="text-center space-y-1">
                  <div className="text-3xl font-black text-emerald-400">
                    {analytics.summary.total_village_homestay_bookings.toLocaleString()}
                  </div>
                  <div className="text-xs text-slate-300">Village Homestay Bookings</div>
                </div>
                <div className="text-center space-y-1">
                  <div className="text-3xl font-black text-white">
                    {formatINR(analytics.summary.local_revenue_generated_inr)}
                  </div>
                  <div className="text-xs text-slate-300">Local Revenue Generated</div>
                </div>
                <div className="text-center space-y-1">
                  <div className="text-3xl font-black text-teal-400">
                    {analytics.summary.crowd_pressure_reduction_darjeeling_percent}%
                  </div>
                  <div className="text-xs text-slate-300">Darjeeling Pressure Relief</div>
                </div>
              </div>
            </div>

            {/* Destination Flow Impact (from /api/impact) */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-rose-500" />
                    <span>Darjeeling → Rural Village Flow Impact</span>
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Live crowd redistribution metrics from <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">/api/impact/destination/darjeeling</code>
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-black ${darjImpact.is_congested_hub ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300' : 'bg-emerald-100 text-emerald-800'}`}>
                  {darjImpact.is_congested_hub ? '🔴 HIGH PRESSURE HUB' : '🟢 LOW PRESSURE'}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                {darjImpact.key_metrics.map((m, i) => (
                  <div key={i} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 space-y-1">
                    <span className="text-slate-400 uppercase text-[10px] font-bold">{m.label}</span>
                    <div className="font-black text-base text-slate-900 dark:text-white">{m.value}</div>
                    <span className="text-slate-500">{m.sub}</span>
                  </div>
                ))}
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 space-y-1">
                  <span className="text-slate-400 uppercase text-[10px] font-bold">Pressure Relief</span>
                  <div className="font-black text-base text-emerald-600 dark:text-emerald-400">
                    -{darjImpact.crowd_pressure_reduction_percent}%
                  </div>
                  <span className="text-slate-500">Mall Road congestion reduced</span>
                </div>
                <div className="p-4 rounded-2xl bg-teal-50 dark:bg-teal-950/20 border border-teal-500/20 space-y-1">
                  <span className="text-teal-600 dark:text-teal-400 uppercase text-[10px] font-bold">Community Fund</span>
                  <div className="font-black text-base text-teal-600 dark:text-teal-400">
                    {formatINR(darjImpact.community_fund_generated_inr)}
                  </div>
                  <span className="text-teal-700/70 dark:text-teal-400/70 text-[10px]">Village eco-infrastructure</span>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Beneficiary Villages</span>
                <div className="flex flex-wrap gap-2">
                  {darjImpact.beneficiary_villages.map((v, i) => (
                    <span key={i} className="text-xs bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-500/20 px-3 py-1 rounded-full font-semibold flex items-center gap-1">
                      <MapPin className="w-3 h-3" /><span>{v}</span>
                    </span>
                  ))}
                </div>
              </div>

              <blockquote className="text-sm text-slate-600 dark:text-slate-400 italic border-l-4 border-emerald-500 pl-4 py-1">
                {darjImpact.narrative_summary}
              </blockquote>
            </div>

            {/* Village-Level Distribution */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-500" />
                <span>Village-Level Tourist Distribution</span>
              </h2>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
                    <tr>
                      <th className="pb-3">Village / Panchayat Zone</th>
                      <th className="pb-3">Verified Stays</th>
                      <th className="pb-3">Tourist Arrivals</th>
                      <th className="pb-3">Local Spend</th>
                      <th className="pb-3 text-teal-600">Eco Fund</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {analytics.village_distribution.map((vd: any, i: number) => (
                      <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                        <td className="py-3 font-bold text-slate-900 dark:text-white">{vd.village}</td>
                        <td className="py-3 text-slate-600 dark:text-slate-400">{vd.verified_homestays}</td>
                        <td className="py-3 font-medium text-blue-600 dark:text-blue-400">{vd.tourist_arrivals}</td>
                        <td className="py-3 font-semibold text-slate-900 dark:text-white">{formatINR(vd.local_spend_inr)}</td>
                        <td className="py-3 font-semibold text-teal-600 dark:text-teal-400">{formatINR(vd.fund_contribution_inr)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Community Fund Usage */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <HeartHandshake className="w-5 h-5 text-teal-600" />
                <span>Gram Panchayat Community Fund Ledger</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                <div className="p-4 rounded-2xl bg-teal-50 dark:bg-teal-950/20 border border-teal-500/20 space-y-1">
                  <span className="text-teal-600 dark:text-teal-400 uppercase text-[10px] font-bold">Total Collected</span>
                  <div className="font-black text-lg text-teal-700 dark:text-teal-300">
                    {formatINR(analytics.community_fund_expenditure.total_collected_inr)}
                  </div>
                  <span className="text-teal-600/70 dark:text-teal-400/70">5% from all homestay bookings</span>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 space-y-1">
                  <span className="text-slate-400 uppercase text-[10px] font-bold">Deployed on Projects</span>
                  <div className="font-black text-lg text-slate-900 dark:text-white">
                    {formatINR(analytics.community_fund_expenditure.total_spent_on_projects_inr)}
                  </div>
                  <span className="text-slate-500">{analytics.community_fund_expenditure.active_projects_count} active projects funded</span>
                </div>
                <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-500/20 space-y-1">
                  <span className="text-emerald-600 dark:text-emerald-400 uppercase text-[10px] font-bold">Reserve Balance</span>
                  <div className="font-black text-lg text-emerald-700 dark:text-emerald-300">
                    {formatINR(analytics.community_fund_expenditure.reserve_balance_inr)}
                  </div>
                  <span className="text-emerald-600/70 dark:text-emerald-400/70">Available for new proposals</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
