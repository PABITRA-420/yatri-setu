'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  TrendingUp, 
  ArrowLeft, 
  DollarSign, 
  HeartHandshake, 
  ShieldCheck, 
  Calendar, 
  Download,
  Info,
  CheckCircle2,
  Landmark,
  PieChart
} from 'lucide-react';
import { fetchHostEarnings } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { HostEarningsSummary } from '@/types';

export default function HostEarningsPage() {
  const [earnings, setEarnings] = useState<HostEarningsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchHostEarnings('host-kalim-01');
        setEarnings(data);
      } catch (err) {
        console.error('Failed to load earnings:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <Link href="/host/dashboard" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-amber-600 transition-colors mb-2">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Dashboard</span>
            </Link>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
              Host Financials & Transparent Revenue
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Deterministic 90-5-5 revenue split: 90% Host, 5% Gram Panchayat, 5% Tech Infrastructure
            </p>
          </div>

          <Link
            href="/panchayat"
            className="px-4 py-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 font-bold text-xs flex items-center gap-1.5"
          >
            <Landmark className="w-4 h-4" />
            <span>View Panchayat Fund Use</span>
          </Link>
        </div>

        {loading || !earnings ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-amber-600 mx-auto" />
          </div>
        ) : (
          <>
            {/* 4 Financial KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Gross Booking Value</span>
                <div className="text-2xl font-black text-slate-900 dark:text-white">
                  {formatINR(earnings.gross_value_inr)}
                </div>
                <span className="text-[11px] text-slate-500 block">
                  Across {earnings.total_bookings} verified reservations
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1 bg-gradient-to-br from-emerald-500/5 to-transparent border-emerald-500/30">
                <span className="text-[10px] uppercase font-bold text-emerald-600 dark:text-emerald-400 tracking-wider">
                  Net Host Income (90%)
                </span>
                <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                  {formatINR(earnings.net_host_income_inr)}
                </div>
                <span className="text-[11px] text-emerald-700 dark:text-emerald-300 font-medium block">
                  Zero hidden OTA cuts
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-teal-600 dark:text-teal-400 tracking-wider">
                  Community Fund (5%)
                </span>
                <div className="text-2xl font-black text-teal-600 dark:text-teal-400">
                  {formatINR(earnings.community_contribution_inr)}
                </div>
                <span className="text-[11px] text-teal-700 dark:text-teal-300 font-medium block">
                  For village footpaths & sanitation
                </span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                  Platform Fee (5%)
                </span>
                <div className="text-2xl font-black text-slate-700 dark:text-slate-300">
                  {formatINR(earnings.platform_fee_inr)}
                </div>
                <span className="text-[11px] text-slate-500 block">
                  Cloud hosting & crowd engines
                </span>
              </div>
            </div>

            {/* Visual Revenue Formula Explainer */}
            <div className="bg-gradient-to-r from-amber-500/10 via-teal-500/10 to-emerald-500/10 rounded-2xl p-6 border border-amber-500/20 space-y-3">
              <h2 className="font-extrabold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                <PieChart className="w-4 h-4 text-amber-600" />
                <span>Deterministic SIH 2026 Settlement Equation</span>
              </h2>
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono bg-white/70 dark:bg-slate-900/70 p-4 rounded-xl border border-slate-200/60 dark:border-slate-800">
                <div className="text-center sm:text-left">
                  <span className="text-slate-500 block text-[10px]">Gross Reservation</span>
                  <span className="font-black text-slate-900 dark:text-white text-sm">₹10,000 (100%)</span>
                </div>
                <span className="text-slate-400 font-bold">=</span>
                <div className="text-center sm:text-left">
                  <span className="text-emerald-600 block text-[10px]">Host Net Income</span>
                  <span className="font-black text-emerald-600 text-sm">₹9,000 (90%)</span>
                </div>
                <span className="text-slate-400 font-bold">+</span>
                <div className="text-center sm:text-left">
                  <span className="text-teal-600 block text-[10px]">Panchayat Eco Fund</span>
                  <span className="font-black text-teal-600 text-sm">₹500 (5%)</span>
                </div>
                <span className="text-slate-400 font-bold">+</span>
                <div className="text-center sm:text-left">
                  <span className="text-slate-500 block text-[10px]">Platform Maintenance</span>
                  <span className="font-black text-slate-700 dark:text-slate-300 text-sm">₹500 (5%)</span>
                </div>
              </div>
            </div>

            {/* Individual Ledger Records */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-black text-slate-900 dark:text-white">
                  Booking Settlement Ledger
                </h2>
                <span className="text-xs text-slate-400 font-medium">All payouts direct-to-host bank prototype</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
                    <tr>
                      <th className="pb-3">Stay & Guest</th>
                      <th className="pb-3">Duration</th>
                      <th className="pb-3">Gross Total</th>
                      <th className="pb-3 text-teal-600">Panchayat 5%</th>
                      <th className="pb-3">Platform 5%</th>
                      <th className="pb-3 font-bold text-emerald-600 text-right">Net Host Payout</th>
                      <th className="pb-3 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {earnings.records.map((r) => (
                      <tr key={r.booking_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                        <td className="py-3">
                          <div className="font-bold text-slate-900 dark:text-white">{r.guest_name}</div>
                          <div className="text-[10px] text-slate-400 font-mono">{r.booking_id}</div>
                        </td>
                        <td className="py-3 text-slate-600 dark:text-slate-400">
                          {r.nights} nights ({r.check_in_date})
                        </td>
                        <td className="py-3 font-medium text-slate-700 dark:text-slate-300">
                          {formatINR(r.gross_booking_value)}
                        </td>
                        <td className="py-3 font-semibold text-teal-600 dark:text-teal-400">
                          {formatINR(r.community_fund_contribution)}
                        </td>
                        <td className="py-3 text-slate-400">
                          {formatINR(r.platform_fee)}
                        </td>
                        <td className="py-3 text-right font-black text-emerald-600 dark:text-emerald-400 text-sm">
                          {formatINR(r.net_host_earning)}
                        </td>
                        <td className="py-3 text-right">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            r.payout_status === 'DISBURSED'
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                              : 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300'
                          }`}>
                            {r.payout_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
