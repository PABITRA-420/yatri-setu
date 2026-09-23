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
  DollarSign,
  Bell,
  ShieldAlert,
  Shield,
  Activity,
  Layers,
  Lock
} from 'lucide-react';
import { fetchPanchayatDashboard, acknowledgePanchayatNotification, resolvePanchayatNotification } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { PanchayatDashboard, PanchayatNotification } from '@/types';
import { Breadcrumbs } from '@/components/Breadcrumbs';
import { SparklineChart } from '@/components/SparklineChart';

export default function PanchayatPortalPage() {
  const [dashboard, setDashboard] = useState<PanchayatDashboard | null>(null);
  const [selectedDestination, setSelectedDestination] = useState<string>('kalimpong');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const destinations = [
    { id: 'kalimpong', name: 'Kalimpong' },
    { id: 'lava', name: 'Lava' },
    { id: 'lolegaon', name: 'Lolegaon' },
    { id: 'mirik', name: 'Mirik' },
    { id: 'rishop', name: 'Rishop' },
    { id: 'darjeeling', name: 'Darjeeling' },
  ];

  async function loadDashboard(destId: string) {
    setLoading(true);
    try {
      const data = await fetchPanchayatDashboard();
      setDashboard(data);
    } catch (err) {
      console.error('Failed to load panchayat dashboard:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard(selectedDestination);
  }, [selectedDestination]);

  async function handleAcknowledge(notifId: string) {
    setActionLoading(notifId);
    try {
      await acknowledgePanchayatNotification(notifId, 'Panchayat Desk Nodal');
      await loadDashboard(selectedDestination);
    } catch (err) {
      console.error('Failed to acknowledge notification:', err);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleResolve(notifId: string) {
    setActionLoading(notifId);
    try {
      await resolvePanchayatNotification(notifId, 'Panchayat Desk Nodal', 'Capacity and tourist flow conditions normalized.');
      await loadDashboard(selectedDestination);
    } catch (err) {
      console.error('Failed to resolve notification:', err);
    } finally {
      setActionLoading(null);
    }
  }

  return (
    <div className="min-h-screen bg-[#0A0D12] text-white py-8 px-4 sm:px-8 lg:px-12">
      <div className="max-w-[1440px] mx-auto space-y-8">
        <Breadcrumbs />
        
        {/* Official Civic Authority Header */}
        <div className="bg-stone-900/90 backdrop-blur-xl text-white rounded-3xl p-6 sm:p-8 shadow-2xl border border-emerald-500/30 relative overflow-hidden">
          <div className="absolute -top-12 -right-12 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-emerald-600/20 border-2 border-emerald-400/40 flex items-center justify-center text-emerald-400 shadow-inner">
                <Landmark className="w-8 h-8" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[10px] uppercase tracking-widest font-black bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded border border-emerald-500/40">
                    Civic Administrative Portal
                  </span>
                  <span className="text-xs text-stone-400 font-mono">SIH &apos;26 GOV NODE</span>
                  {dashboard?.provenance && (
                    <span className="text-[9px] bg-stone-800 text-stone-300 px-2 py-0.5 rounded border border-stone-700 font-mono">
                      {dashboard.provenance}
                    </span>
                  )}
                </div>
                <h1 className="text-2xl sm:text-3xl font-black tracking-tight mt-1">
                  Gram Panchayat Tourism & Ecology Desk
                </h1>
                <p className="text-xs sm:text-sm text-stone-300 mt-0.5">
                  {dashboard?.panchayat_name || 'Kalimpong District Apex Nodal'} • {dashboard?.block || 'Block II'}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <Link
                href="/panchayat/verifications"
                className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-stone-950 font-black text-xs shadow-md shadow-emerald-500/20 flex items-center gap-1.5 transition-all active:scale-95"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Audit Queue ({dashboard?.pending_verifications_count || 0})</span>
              </Link>
              <Link
                href="/panchayat/analytics"
                className="px-4 py-2.5 rounded-xl bg-stone-800 hover:bg-stone-700 text-white font-bold text-xs border border-stone-700 flex items-center gap-1.5 transition-all"
              >
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <span>Economic Impact</span>
              </Link>
            </div>
          </div>

          {/* Destination Selector Strip */}
          <div className="mt-6 pt-4 border-t border-stone-800/80 flex flex-wrap items-center gap-2 relative z-10">
            <span className="text-xs font-bold text-stone-400 uppercase tracking-wider mr-2">Jurisdiction Desk:</span>
            {destinations.map((d) => (
              <button
                key={d.id}
                onClick={() => setSelectedDestination(d.id)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition active:scale-95 ${
                  selectedDestination === d.id
                    ? 'bg-emerald-500 text-stone-950 shadow-sm'
                    : 'bg-stone-800/80 text-stone-300 hover:bg-stone-700'
                }`}
              >
                {d.name}
              </button>
            ))}
          </div>
        </div>

        {/* Capacity Warning Banner if Elevated */}
        {dashboard?.capacity_warning && (
          <div className="bg-amber-500/10 border-2 border-amber-500/40 rounded-3xl p-5 text-amber-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0 mt-0.5">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-sm text-amber-300 uppercase tracking-wide">
                    {dashboard.capacity_warning.status} Capacity Advisory
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-amber-900/50 text-amber-200 font-mono">
                    Occupancy: {dashboard.capacity_warning.occupancy_percent}%
                  </span>
                </div>
                <p className="text-xs text-amber-200/90 mt-1">
                  {dashboard.capacity_warning.advisory}
                </p>
                <span className="text-[10px] text-amber-400 italic block mt-0.5">
                  {dashboard.capacity_warning.disclaimer}
                </span>
              </div>
            </div>
            <div className="shrink-0 px-3 py-1.5 rounded-xl bg-amber-500 text-stone-950 text-xs font-black">
              {dashboard.capacity_warning.available_units} Units Available
            </div>
          </div>
        )}

        {loading || !dashboard ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-emerald-500 mx-auto" />
          </div>
        ) : (
          <>
            {/* Primary KPI Grid (8 Administrative Metrics) */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider">Verified Homestays</span>
                  <span className="text-xs font-bold text-emerald-400">↑ 12%</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-emerald-400 font-mono">
                    {dashboard.verified_homestays_count}
                  </div>
                  <SparklineChart data={[12, 14, 15, 18, 20, 22, dashboard.verified_homestays_count]} color="#10B981" height={28} />
                </div>
                <span className="text-[11px] text-stone-400 block">Registered village units</span>
              </div>

              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-amber-400 tracking-wider">Pending Audit</span>
                  <span className="text-xs font-bold text-amber-400">Action Req</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-amber-400 font-mono">
                    {dashboard.pending_verifications_count}
                  </div>
                  <SparklineChart data={[5, 4, 6, 3, 4, 2, dashboard.pending_verifications_count]} color="#F59E0B" height={28} type="bar" />
                </div>
                <Link href="/panchayat/verifications" className="text-[11px] text-amber-400 font-bold block hover:underline">
                  Needs field inspection →
                </Link>
              </div>

              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider">Local Guides</span>
                  <span className="text-xs font-bold text-emerald-400">↑ 8%</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-white font-mono">
                    {dashboard.local_guides_count}
                  </div>
                  <SparklineChart data={[10, 12, 12, 14, 15, 16, dashboard.local_guides_count]} color="#3B82F6" height={28} />
                </div>
                <span className="text-[11px] text-stone-400 block">Naturalists & porters</span>
              </div>

              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider">Experiences</span>
                  <span className="text-xs font-bold text-emerald-400">↑ 15%</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-white font-mono">
                    {dashboard.total_experiences_count}
                  </div>
                  <SparklineChart data={[8, 9, 11, 12, 13, 14, dashboard.total_experiences_count]} color="#8B5CF6" height={28} />
                </div>
                <span className="text-[11px] text-stone-400 block">Crafts, birding, farm tours</span>
              </div>

              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider">Tourist Arrivals</span>
                  <span className="text-xs font-bold text-emerald-400">↑ 24%</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-blue-400 font-mono">
                    {dashboard.tourist_arrivals_this_month}
                  </div>
                  <SparklineChart data={[140, 180, 210, 260, 310, 340, dashboard.tourist_arrivals_this_month]} color="#3B82F6" height={28} />
                </div>
                <span className="text-[11px] text-stone-400 block">This calendar month</span>
              </div>

              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider">Village Revenue</span>
                  <span className="text-xs font-bold text-emerald-400">↑ 32%</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-white font-mono">
                    {formatINR(dashboard.local_booking_revenue_inr)}
                  </div>
                  <SparklineChart data={[120000, 180000, 250000, 310000, 420000, dashboard.local_booking_revenue_inr]} color="#10B981" height={28} />
                </div>
                <span className="text-[11px] text-emerald-400 font-semibold block">Retained in rural hamlets</span>
              </div>

              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2 bg-gradient-to-br from-teal-500/10 to-transparent border-teal-500/30">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-teal-400 tracking-wider">Community Fund</span>
                  <span className="text-xs font-bold text-emerald-400">5% Levy</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-teal-400 font-mono">
                    {formatINR(dashboard.community_fund_balance_inr)}
                  </div>
                  <SparklineChart data={[20000, 35000, 48000, 56000, 68000, dashboard.community_fund_balance_inr]} color="#14B8A6" height={28} />
                </div>
                <span className="text-[11px] text-teal-300 font-medium block">5% civic levy reserve</span>
              </div>

              <div className="bg-stone-900/80 p-5 rounded-2xl border border-white/10 shadow-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider">Pressure Relief</span>
                  <span className="text-xs font-bold text-emerald-400">Optimal</span>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-emerald-400 font-mono">
                    +{(dashboard.tourism_pressure_relief_index * 100).toFixed(0)}%
                  </div>
                  <SparklineChart data={[0.2, 0.25, 0.3, 0.35, 0.4, dashboard.tourism_pressure_relief_index]} color="#10B981" height={28} />
                </div>
                <span className="text-[11px] text-stone-400 block">Darjeeling overload relief</span>
              </div>
            </div>

            {/* M7F Safety Integration & Notifications Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Civic Safety Summary Card */}
              <div className="bg-stone-900/80 rounded-3xl p-6 border border-white/10 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-red-400" />
                    <h2 className="text-base font-black text-white">
                      Jurisdiction Safety & Emergency Overview
                    </h2>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 font-mono">
                    Zero PII Exemption
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-stone-950/60 p-4 rounded-2xl border border-white/5 text-center">
                  <div>
                    <span className="text-[10px] text-stone-400 block uppercase">Active SOS</span>
                    <span className="text-lg font-black text-red-400 font-mono">
                      {(dashboard as any).active_safety_incidents?.active_sos_alerts || dashboard.safety_summary?.active_sos || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-400 block uppercase">Active Responders</span>
                    <span className="text-lg font-black text-emerald-400 font-mono">
                      {(dashboard as any).active_safety_incidents?.active_responders || dashboard.safety_summary?.active_responders || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-400 block uppercase">Avg Response</span>
                    <span className="text-lg font-black text-amber-400 font-mono">
                      {(dashboard as any).active_safety_incidents?.avg_response_time_minutes || dashboard.safety_summary?.avg_response_time_minutes || 4}m
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-400 block uppercase">24h Incidents</span>
                    <span className="text-lg font-black text-blue-400 font-mono">
                      {(dashboard as any).active_safety_incidents?.incidents_24h || dashboard.safety_summary?.incidents_24h || 0}
                    </span>
                  </div>
                </div>


                <p className="text-xs text-stone-400 leading-relaxed">
                  Gram Panchayat desk operators receive non-PII telemetry feeds for active distress signals within village boundaries to coordinate local mountain rescue teams.
                </p>

                <div className="flex items-center justify-between pt-2">
                  <Link
                    href="/safety/sos"
                    className="text-xs font-bold text-red-400 hover:text-red-300 flex items-center gap-1"
                  >
                    <span>Open Live SOS Telemetry Desk</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                  <span className="text-[10px] text-stone-500">M7F Privacy Protocol Enforced</span>
                </div>
              </div>

              {/* Active Notifications & Crowd Capacity Alerts */}
              <div className="bg-stone-900/80 rounded-3xl p-6 border border-white/10 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bell className="w-5 h-5 text-amber-400" />
                    <h2 className="text-base font-black text-white">
                      Civic Capacity & Flow Alerts
                    </h2>
                  </div>
                  <span className="text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded-full border border-amber-500/20">
                    {dashboard.notifications?.length || 0} Active Alerts
                  </span>
                </div>

                <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
                  {dashboard.notifications && dashboard.notifications.length > 0 ? (
                    dashboard.notifications.map((n) => (
                      <div
                        key={n.notification_id}
                        className={`p-3.5 rounded-2xl border text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${
                          n.severity === 'CRITICAL'
                            ? 'bg-red-500/10 border-red-500/30 text-red-200'
                            : n.severity === 'WARNING'
                            ? 'bg-amber-500/10 border-amber-500/30 text-amber-200'
                            : 'bg-stone-950/60 border-white/5 text-stone-300'
                        }`}
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-white">{n.title}</span>
                            <span className="text-[9px] uppercase px-1.5 py-0.2 bg-stone-950 rounded border border-white/10 font-mono">
                              {n.severity}
                            </span>
                          </div>
                          <p className="text-[11px] mt-0.5 text-stone-300 leading-snug">{n.message}</p>
                        </div>

                        <div className="flex items-center gap-1.5 shrink-0 self-end sm:self-auto">
                          {n.status === 'NEW' && (
                            <button
                              onClick={() => handleAcknowledge(n.notification_id)}
                              disabled={actionLoading === n.notification_id}
                              className="px-2.5 py-1 rounded-lg bg-stone-800 hover:bg-stone-700 text-stone-200 text-[10px] font-bold border border-white/10"
                            >
                              Ack
                            </button>
                          )}
                          <button
                            onClick={() => handleResolve(n.notification_id)}
                            disabled={actionLoading === n.notification_id}
                            className="px-2.5 py-1 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-stone-950 text-[10px] font-bold"
                          >
                            Resolve
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="py-8 text-center text-xs text-stone-500">
                      No active capacity alerts for this jurisdiction.
                    </div>
                  )}
                </div>

              </div>

            </div>
          </>
        )}

      </div>
    </div>
  );
}
