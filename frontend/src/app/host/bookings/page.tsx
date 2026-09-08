'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Users, 
  Calendar, 
  ShieldCheck, 
  ArrowLeft, 
  Phone, 
  QrCode, 
  CheckCircle2, 
  TrendingUp, 
  Clock,
  ExternalLink
} from 'lucide-react';
import { fetchHostEarnings } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { HostEarningsSummary } from '@/types';

export default function HostBookingsPage() {
  const [earnings, setEarnings] = useState<HostEarningsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedBookingQr, setSelectedBookingQr] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchHostEarnings('host-kalim-01');
        setEarnings(data);
      } catch (err) {
        console.error('Failed to load host bookings:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <Link href="/host/dashboard" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-amber-600 transition-colors mb-2">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Dashboard</span>
            </Link>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
              Guest Reservations & Travel Passes
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Direct traveler bookings with verified digital travel passes and guaranteed 90% payout
            </p>
          </div>

          <Link
            href="/host/earnings"
            className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 font-bold text-xs flex items-center gap-1.5"
          >
            <TrendingUp className="w-4 h-4 text-emerald-500" />
            <span>Earnings Breakdown</span>
          </Link>
        </div>

        {loading || !earnings ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-amber-600 mx-auto" />
          </div>
        ) : (
          <div className="space-y-4">
            {earnings.records.map((rec) => (
              <div
                key={rec.booking_id}
                className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4 hover:shadow-md transition-all"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/50 px-2 py-0.5 rounded">
                        {rec.booking_id}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        rec.payout_status === 'DISBURSED'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300'
                      }`}>
                        {rec.payout_status === 'DISBURSED' ? 'PAYOUT DISBURSED' : 'ESCROW SECURED'}
                      </span>
                    </div>
                    <h2 className="text-base font-extrabold text-slate-900 dark:text-white">
                      {rec.guest_name}
                    </h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {rec.homestay_name}
                    </p>
                  </div>

                  <div className="text-left sm:text-right space-y-0.5">
                    <div className="text-lg font-black text-emerald-600 dark:text-emerald-400">
                      {formatINR(rec.net_host_earning)}
                    </div>
                    <span className="text-[10px] text-slate-400 block">
                      Net Host Payout (90%) • Gross {formatINR(rec.gross_booking_value)}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Stay Dates</span>
                    <div className="font-semibold text-slate-900 dark:text-white mt-0.5 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-amber-500" />
                      <span>{rec.check_in_date} → {rec.check_out_date} ({rec.nights} nights)</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Panchayat Community Contribution</span>
                    <div className="font-semibold text-teal-600 dark:text-teal-400 mt-0.5">
                      {formatINR(rec.community_fund_contribution)} (5% for village eco fund)
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Platform Tech Fee</span>
                    <div className="font-semibold text-slate-600 dark:text-slate-300 mt-0.5">
                      {formatINR(rec.platform_fee)} (5% maintenance)
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Phone className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Traveler SMS contact & emergency telemetry active</span>
                  </div>

                  <button
                    type="button"
                    onClick={() => setSelectedBookingQr(selectedBookingQr === rec.booking_id ? null : rec.booking_id)}
                    className="px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-700 dark:text-amber-400 hover:bg-amber-500/20 font-bold text-xs flex items-center gap-1.5"
                  >
                    <QrCode className="w-3.5 h-3.5" />
                    <span>{selectedBookingQr === rec.booking_id ? 'Hide Travel Pass' : 'Inspect Digital Pass'}</span>
                  </button>
                </div>

                {selectedBookingQr === rec.booking_id && (
                  <div className="p-4 rounded-xl bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 text-xs space-y-2">
                    <div className="flex items-center gap-2 font-bold text-amber-800 dark:text-amber-300">
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                      <span>Encrypted Digital Travel Pass Payload</span>
                    </div>
                    <p className="font-mono text-[11px] text-slate-700 dark:text-slate-300 break-all bg-white dark:bg-slate-900 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                      YATRISETU://PASS/{rec.booking_id}/GUEST/{encodeURIComponent(rec.guest_name)}/VILLAGE/KalimpongBlockII/PANCHAYAT_VERIFIED/2026
                    </p>
                    <span className="text-[10px] text-slate-500 block">
                      This QR pass allows tourists seamless transit through regional checkposts without municipal bottleneck queues.
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
