'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Landmark, 
  ShieldCheck, 
  Clock, 
  Users, 
  Sparkles, 
  TrendingUp, 
  Award, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight,
  FileText,
  MapPin,
  Building2,
  Compass,
  DollarSign
} from 'lucide-react';
import { fetchPanchayatDashboard } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { PanchayatDashboard } from '@/types';

export default function PanchayatPortalPage() {
  const [dashboard, setDashboard] = useState<PanchayatDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchPanchayatDashboard();
        setDashboard(data);
      } catch (err) {
        console.error('Failed to load panchayat dashboard:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Official Civic Authority Header */}
        <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl border-2 border-emerald-500/30 relative overflow-hidden">
          <div className="absolute -top-12 -right-12 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-emerald-600/20 border-2 border-emerald-400/40 flex items-center justify-center text-emerald-400 shadow-inner">
                <Landmark className="w-8 h-8" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] uppercase tracking-widest font-black bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded border border-emerald-500/40">
                    Civic Administrative Portal
                  </span>
                  <span className="text-xs text-slate-400 font-mono">SIH &apos;26 GOV NODE</span>
                </div>
                <h1 className="text-2xl sm:text-3xl font-black tracking-tight mt-1">
                  Gram Panchayat Tourism & Ecology Desk
                </h1>
                <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
                  Kalimpong District Apex Nodal • Blocks II & Neora Valley Ranges
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <Link
                href="/panchayat/verifications"
                className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black text-xs shadow-md shadow-emerald-500/20 flex items-center gap-1.5 transition-all active:scale-95"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Audit Queue ({dashboard?.pending_verifications_count || 0})</span>
              </Link>
              <Link
                href="/panchayat/analytics"
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs border border-slate-700 flex items-center gap-1.5 transition-all"
              >
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <span>Economic Impact</span>
              </Link>
            </div>
          </div>
        </div>

        {loading || !dashboard ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-emerald-600 mx-auto" />
          </div>
        ) : (
          <>
            {/* Primary KPI Grid (8 Administrative Metrics) */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Verified Homestays</span>
                <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                  {dashboard.verified_homestays_count}
                </div>
                <span className="text-[11px] text-slate-500 block">
                  Registered village units
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-amber-500 tracking-wider">Pending Audit</span>
                <div className="text-2xl font-black text-amber-500">
                  {dashboard.pending_verifications_count}
                </div>
                <Link href="/panchayat/verifications" className="text-[11px] text-amber-600 dark:text-amber-400 font-bold block hover:underline">
                  Needs field inspection →
                </Link>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Local Guides</span>
                <div className="text-2xl font-black text-slate-900 dark:text-white">
                  {dashboard.local_guides_count}
                </div>
                <span className="text-[11px] text-slate-500 block">
                  Naturalists & porters
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Experiences Listed</span>
                <div className="text-2xl font-black text-slate-900 dark:text-white">
                  {dashboard.total_experiences_count}
                </div>
                <span className="text-[11px] text-slate-500 block">
                  Crafts, birding, farm tours
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Tourist Arrivals</span>
                <div className="text-2xl font-black text-blue-600 dark:text-blue-400">
                  {dashboard.tourist_arrivals_this_month}
                </div>
                <span className="text-[11px] text-slate-500 block">
                  This calendar month
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Village Revenue</span>
                <div className="text-2xl font-black text-slate-900 dark:text-white">
                  {formatINR(dashboard.local_booking_revenue_inr)}
                </div>
                <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold block">
                  Retained in rural hamlets
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1 bg-gradient-to-br from-teal-500/5 to-transparent border-teal-500/30">
                <span className="text-[10px] uppercase font-bold text-teal-600 dark:text-teal-400 tracking-wider">Community Fund</span>
                <div className="text-2xl font-black text-teal-600 dark:text-teal-400">
                  {formatINR(dashboard.community_fund_balance_inr)}
                </div>
                <span className="text-[11px] text-teal-700 dark:text-teal-300 font-medium block">
                  5% civic levy reserve
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Pressure Relief</span>
                <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                  +{(dashboard.tourism_pressure_relief_index * 100).toFixed(0)}%
                </div>
                <span className="text-[11px] text-slate-500 block">
                  Darjeeling overload relief
                </span>
              </div>
            </div>

            {/* Live Community Fund Projects Section */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-teal-600" />
                    <span>Gram Panchayat Community Infrastructure Projects</span>
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Funded exclusively by the 5% tourist stay contribution
                  </p>
                </div>
                <div className="px-3 py-1 rounded-full bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 border border-teal-500/30 text-xs font-bold font-mono">
                  Fund Balance: {formatINR(dashboard.community_fund_balance_inr)}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dashboard.community_projects.map((proj) => (
                  <div
                    key={proj.id}
                    className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850 space-y-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                          {proj.status}
                        </span>
                        <h3 className="font-extrabold text-sm text-slate-900 dark:text-white mt-1">
                          {proj.title}
                        </h3>
                      </div>
                      <span className="font-black text-sm text-slate-900 dark:text-white shrink-0">
                        {formatINR(proj.budget_inr)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {proj.impact_description}
                    </p>
                    <div className="text-[10px] text-slate-400 pt-1">
                      Completed: {proj.completion_date} • Category: {proj.category}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions to Verification Queue */}
            <div className="bg-gradient-to-r from-emerald-600 via-teal-700 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-6">
              <div className="space-y-1 text-center sm:text-left">
                <h2 className="text-lg font-black">Homestay Verification Queue</h2>
                <p className="text-xs text-emerald-100 max-w-lg">
                  Ensure guest safety, organic waste disposal, and fire preparedness before granting the Panchayat Verified seal.
                </p>
              </div>
              <Link
                href="/panchayat/verifications"
                className="px-6 py-3 rounded-xl bg-white text-slate-900 hover:bg-emerald-50 font-black text-xs shadow-md active:scale-95 transition-all shrink-0"
              >
                Review Pending Applications ({dashboard.pending_verifications_count})
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
