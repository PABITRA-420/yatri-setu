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
      const res = await fetch(`http://localhost:8000/api/panchayat/dashboard?destination_id=${destId}`, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setDashboard(data);
      } else {
        const fallback = await fetchPanchayatDashboard();
        setDashboard(fallback);
      }
    } catch (err) {
      console.error('Failed to load panchayat dashboard:', err);
      const fallback = await fetchPanchayatDashboard();
      setDashboard(fallback);
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
    <div className="min-h-screen bg-[#0A0D12] text-white py-10 px-4 sm:px-8 lg:px-12">
      <div className="max-w-[1440px] mx-auto space-y-8">
        
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
                  <span className="text-xs text-slate-400 font-mono">SIH &apos;26 GOV NODE</span>
                  {dashboard?.provenance && (
                    <span className="text-[9px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">
                      {dashboard.provenance}
                    </span>
                  )}
                </div>
                <h1 className="text-2xl sm:text-3xl font-black tracking-tight mt-1">
                  Gram Panchayat Tourism & Ecology Desk
                </h1>
                <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
                  {dashboard?.panchayat_name || 'Kalimpong District Apex Nodal'} • {dashboard?.block || 'Block II'}
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

          {/* Destination Selector Strip */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-2 relative z-10">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-2">Jurisdiction Desk:</span>
            {destinations.map((d) => (
              <button
                key={d.id}
                onClick={() => setSelectedDestination(d.id)}
                className={`px-3 py-1 rounded-xl text-xs font-bold transition ${
                  selectedDestination === d.id
                    ? 'bg-emerald-500 text-slate-950 shadow-sm'
                    : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {d.name}
              </button>
            ))}
          </div>
        </div>

        {/* Capacity Warning Banner if Elevated */}
        {dashboard?.capacity_warning && (
          <div className="bg-amber-500/10 border-2 border-amber-500/40 rounded-3xl p-5 text-amber-900 dark:text-amber-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-amber-500/20 text-amber-600 shrink-0 mt-0.5">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-sm text-amber-800 dark:text-amber-300 uppercase tracking-wide">
                    {dashboard.capacity_warning.status} Capacity Advisory
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-amber-200/50 dark:bg-amber-900/50 text-amber-800 dark:text-amber-200 font-mono">
                    Occupancy: {dashboard.capacity_warning.occupancy_percent}%
                  </span>
                </div>
                <p className="text-xs text-amber-800/90 dark:text-amber-200/90 mt-1">
                  {dashboard.capacity_warning.advisory}
                </p>
                <span className="text-[10px] text-amber-600 dark:text-amber-400 italic block mt-0.5">
                  {dashboard.capacity_warning.disclaimer}
                </span>
              </div>
            </div>
            <div className="shrink-0 px-3 py-1.5 rounded-xl bg-amber-500 text-slate-950 text-xs font-black">
              {dashboard.capacity_warning.available_units} Units Available
            </div>
          </div>
        )}

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

            {/* M7F Safety Integration & Notifications Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Civic Safety Summary Card (M7F) */}
              <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-red-500" />
                    <h2 className="text-base font-black text-slate-900 dark:text-white">
                      Jurisdiction Safety & Emergency Overview
                    </h2>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 font-mono">
                    Zero PII Exemption
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-center">
                    <div className="text-xl font-black text-slate-900 dark:text-white">
                      {dashboard.safety_summary?.active_safety_incidents || 0}
                    </div>
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Active Incidents</span>
                  </div>
                  <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-center">
                    <div className="text-xl font-black text-red-600 dark:text-red-400">
                      {dashboard.safety_summary?.critical_safety_incidents || 0}
                    </div>
                    <span className="text-[10px] text-red-500 font-bold uppercase">Critical</span>
                  </div>
                  <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-center">
                    <div className="text-xl font-black text-amber-600 dark:text-amber-400">
                      {dashboard.safety_summary?.escalation_required_incidents || 0}
                    </div>
                    <span className="text-[10px] text-amber-500 font-bold uppercase">Escalated</span>
                  </div>
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-center">
                    <div className="text-xl font-black text-emerald-600 dark:text-emerald-400">
                      {dashboard.safety_summary?.resolved_safety_incidents || 0}
                    </div>
                    <span className="text-[10px] text-emerald-500 font-bold uppercase">Resolved</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                  <Lock className="w-4 h-4 text-slate-400 shrink-0" />
                  <span>Tourist names, phones, and exact GPS are restricted to police/command dispatch desks.</span>
                </div>
              </div>

              {/* Operational Advisory Notifications */}
              <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bell className="w-5 h-5 text-amber-500" />
                    <h2 className="text-base font-black text-slate-900 dark:text-white">
                      Civic Operational Advisories
                    </h2>
                  </div>
                  <span className="text-xs font-bold text-slate-400">
                    {dashboard.notifications?.length || 0} Alerts
                  </span>
                </div>

                <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                  {dashboard.notifications && dashboard.notifications.length > 0 ? (
                    dashboard.notifications.map((n: PanchayatNotification) => (
                      <div
                        key={n.notification_id}
                        className="p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850 space-y-2 text-xs"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                                n.severity === 'CRITICAL' ? 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300' :
                                n.severity === 'WARNING' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
                                'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                              }`}>
                                {n.severity}
                              </span>
                              <span className="font-bold text-slate-900 dark:text-white">
                                {n.title}
                              </span>
                            </div>
                            <p className="text-slate-600 dark:text-slate-400 mt-1">
                              {n.message}
                            </p>
                          </div>
                          <span className="text-[10px] text-slate-400 shrink-0 font-mono">
                            {n.status}
                          </span>
                        </div>

                        <div className="pt-2 border-t border-slate-200/60 dark:border-slate-800 flex items-center justify-end gap-2">
                          {n.status === 'NEW' && (
                            <button
                              onClick={() => handleAcknowledge(n.notification_id)}
                              disabled={actionLoading === n.notification_id}
                              className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-[10px]"
                            >
                              Acknowledge
                            </button>
                          )}
                          {n.status !== 'RESOLVED' && (
                            <button
                              onClick={() => handleResolve(n.notification_id)}
                              disabled={actionLoading === n.notification_id}
                              className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-[10px]"
                            >
                              Resolve
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-6 text-center text-xs text-slate-400">
                      No active operational advisories for this jurisdiction.
                    </div>
                  )}
                </div>
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
