'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Home, 
  ShieldCheck, 
  TrendingUp, 
  Users, 
  Calendar, 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  AlertTriangle,
  Award,
  Plus,
  Landmark
} from 'lucide-react';
import { fetchHostDashboard } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { Host, HomestayListing, HostEarningsSummary } from '@/types';

export default function HostDashboardPage() {
  const [data, setData] = useState<{
    host: Host;
    listings_count: number;
    listings: HomestayListing[];
    earnings_summary: HostEarningsSummary;
    verification_status: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchHostDashboard('host-kalim-01');
        setData(res);
      } catch (err) {
        console.error('Failed to load host dashboard:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading || !data) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-6">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-amber-600" />
      </div>
    );
  }

  const { host, listings, earnings_summary } = data;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Top Host Profile & Verification Status Card */}
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <img
              src={host.avatar_url}
              alt={host.name}
              className="w-16 h-16 rounded-2xl object-cover border-2 border-amber-500/40 shadow-sm"
            />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                  {host.name}
                </h1>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-bold text-[10px] tracking-wide border border-emerald-500/30 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{host.verification.status}</span>
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {host.village} • {host.panchayat_name}
              </p>
              <div className="flex flex-wrap gap-1.5 mt-2">
                {host.languages.map((l, i) => (
                  <span key={i} className="text-[10px] bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-slate-600 dark:text-slate-400">
                    {l}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <Link
              href="/host/onboarding"
              className="px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              <span>Add Homestay</span>
            </Link>
            <Link
              href="/host/earnings"
              className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 font-bold text-xs flex items-center gap-1.5"
            >
              <TrendingUp className="w-4 h-4 text-blue-500" />
              <span>Earnings</span>
            </Link>
            <Link
              href="/panchayat"
              className="px-4 py-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 font-bold text-xs flex items-center gap-1.5"
            >
              <Landmark className="w-4 h-4" />
              <span>Panchayat Desk</span>
            </Link>
          </div>
        </div>

        {/* 4 Financial & Operational Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold uppercase tracking-wider">Net Host Earnings</span>
              <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">
              {formatINR(earnings_summary.net_host_income_inr)}
            </div>
            <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium block">
              90% direct payout retention
            </span>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold uppercase tracking-wider">Total Stays Booked</span>
              <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600">
                <Users className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">
              {earnings_summary.total_bookings}
            </div>
            <span className="text-[11px] text-slate-500 font-medium block">
              Gross Value: {formatINR(earnings_summary.gross_value_inr)}
            </span>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold uppercase tracking-wider">Panchayat Fund Share</span>
              <div className="p-2 rounded-xl bg-teal-500/10 text-teal-600">
                <Award className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-teal-600 dark:text-teal-400">
              {formatINR(earnings_summary.community_contribution_inr)}
            </div>
            <span className="text-[11px] text-teal-600/80 font-medium block">
              5% to village eco-infrastructure
            </span>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold uppercase tracking-wider">Active Homestays</span>
              <div className="p-2 rounded-xl bg-purple-500/10 text-purple-600">
                <Home className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">
              {listings.length}
            </div>
            <span className="text-[11px] text-purple-600 dark:text-purple-400 font-medium block">
              All Panchayat verified
            </span>
          </div>
        </div>

        {/* Listings Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
              <span>Your Managed Homestay Listings</span>
              <span className="text-xs font-bold text-slate-400">({listings.length})</span>
            </h2>
            <Link
              href="/host/listings"
              className="text-xs font-bold text-amber-600 hover:text-amber-700 flex items-center gap-1"
            >
              <span>View All Listings</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {listings.map((l) => (
              <div
                key={l.id}
                className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between gap-4"
              >
                <div className="flex gap-4">
                  <img
                    src={l.images[0] || 'https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=400&q=80'}
                    alt={l.title}
                    className="w-24 h-24 rounded-xl object-cover shrink-0"
                  />
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-bold text-[9px]">
                        {l.verification_status}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {l.id}
                      </span>
                    </div>
                    <h3 className="font-extrabold text-sm text-slate-900 dark:text-white line-clamp-1">
                      {l.title}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                      {l.tagline}
                    </p>
                    <div className="text-xs font-bold text-slate-900 dark:text-white pt-1">
                      {formatINR(l.price_per_night_inr)} <span className="text-[10px] text-slate-400 font-normal">/ night</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                  <span className="text-slate-500">
                    {l.rooms_count} rooms • Max {l.max_guests} guests
                  </span>
                  <div className="flex items-center gap-2">
                    <Link
                      href="/host/availability"
                      className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs hover:bg-slate-200"
                    >
                      Calendar
                    </Link>
                    <Link
                      href="/host/listings"
                      className="px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-700 dark:text-amber-400 font-bold text-xs hover:bg-amber-500/20"
                    >
                      Edit Listing
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Guest Bookings Preview */}
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-black text-slate-900 dark:text-white">Recent Guest Reservations</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Showing confirmed stays & transparent financial breakdown</p>
            </div>
            <Link
              href="/host/bookings"
              className="text-xs font-bold text-amber-600 hover:text-amber-700 flex items-center gap-1"
            >
              <span>View All Bookings</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
                <tr>
                  <th className="pb-3">Booking ID & Guest</th>
                  <th className="pb-3">Check-in / Out</th>
                  <th className="pb-3">Gross Value</th>
                  <th className="pb-3">Platform (5%)</th>
                  <th className="pb-3">Panchayat (5%)</th>
                  <th className="pb-3 text-right">Net Payout (90%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {earnings_summary.records.map((rec) => (
                  <tr key={rec.booking_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                    <td className="py-3 font-semibold text-slate-900 dark:text-white">
                      <div>{rec.guest_name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{rec.booking_id}</div>
                    </td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">
                      {rec.check_in_date} to {rec.check_out_date} ({rec.nights} nights)
                    </td>
                    <td className="py-3 font-medium text-slate-700 dark:text-slate-300">
                      {formatINR(rec.gross_booking_value)}
                    </td>
                    <td className="py-3 text-slate-400">
                      {formatINR(rec.platform_fee)}
                    </td>
                    <td className="py-3 text-teal-600 font-medium">
                      {formatINR(rec.community_fund_contribution)}
                    </td>
                    <td className="py-3 text-right font-bold text-emerald-600 dark:text-emerald-400">
                      {formatINR(rec.net_host_earning)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
