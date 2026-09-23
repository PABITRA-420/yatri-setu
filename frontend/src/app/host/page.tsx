'use client';

import React from 'react';
import Link from 'next/link';
import { Breadcrumbs } from '@/components/Breadcrumbs';
import { motion } from 'motion/react';
import { 
  Home, 
  Sparkles, 
  ShieldCheck, 
  HeartHandshake, 
  Mic, 
  Calendar, 
  TrendingUp, 
  CheckCircle2, 
  ArrowRight,
  Landmark,
  Compass,
  Users,
  Award
} from 'lucide-react';

export default function HostLandingPage() {
  return (
    <div className="min-h-screen bg-[#0A0D12] text-white py-8 px-4 sm:px-8 lg:px-12">
      <div className="max-w-[1440px] mx-auto space-y-10">
        <Breadcrumbs />

        {/* Hero Section */}
        <div className="relative rounded-[2.5rem] overflow-hidden bg-gradient-to-br from-amber-950 via-stone-900 to-emerald-950 text-white p-8 sm:p-14 shadow-2xl border border-amber-500/20">
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 max-w-3xl space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/20 text-amber-300 text-xs font-bold tracking-wider uppercase border border-amber-500/30">
              <Sparkles className="w-3.5 h-3.5" />
              <span>SIH 2026 • Hyperlocal Rural Economy</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
              Open Your Village Home to Travelers. Keep <span className="text-amber-400">90% of Your Earnings</span>.
            </h1>

            <p className="text-base sm:text-lg text-stone-300 leading-relaxed">
              Yatri Setu actively redirects conscious travelers away from choked urban hotspots like Darjeeling Mall Road into pristine rural hamlets across Kalimpong, Lava, Lolegaon, and Rishop.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-4">
              <Link
                href="/host/onboarding"
                className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-600 hover:to-rose-700 text-white font-extrabold text-xs sm:text-sm shadow-lg shadow-amber-500/25 active:scale-95 transition-all flex items-center gap-2"
              >
                <span>Start Host Onboarding</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <Link
                href="/host/dashboard"
                className="px-6 py-3.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs sm:text-sm backdrop-blur-md border border-white/20 active:scale-95 transition-all flex items-center gap-2"
              >
                <Home className="w-4 h-4 text-amber-400" />
                <span>Host Dashboard (Demo)</span>
              </Link>

              <Link
                href="/panchayat"
                className="px-5 py-3.5 rounded-2xl bg-emerald-900/60 hover:bg-emerald-900/80 text-emerald-200 font-bold text-xs sm:text-sm border border-emerald-500/30 active:scale-95 transition-all flex items-center gap-2"
              >
                <Landmark className="w-4 h-4 text-emerald-400" />
                <span>Panchayat Desk</span>
              </Link>
            </div>
          </div>
        </div>

        {/* 90-5-5 Transparent Economic Model */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            whileHover={{ y: -4, rotate: -0.5 }}
            className="bg-stone-900/80 backdrop-blur-xl p-8 rounded-3xl border border-white/10 shadow-xl relative overflow-hidden group hover:border-amber-500/50 transition-all"
          >
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-black text-2xl mb-4 shadow-inner">
              90%
            </div>
            <h2 className="font-extrabold text-xl text-white">Direct Host Retention</h2>
            <p className="text-xs sm:text-sm text-stone-400 mt-2 leading-relaxed">
              Unlike generic OTAs that take 20-30% commissions, Yatri Setu guarantees that 90% of the entire booking fee goes directly into the rural host's pocket.
            </p>
          </motion.div>

          <motion.div
            whileHover={{ y: -4, rotate: 0.5 }}
            className="bg-stone-900/80 backdrop-blur-xl p-8 rounded-3xl border border-white/10 shadow-xl relative overflow-hidden group hover:border-emerald-500/50 transition-all"
          >
            <div className="w-14 h-14 rounded-2xl bg-teal-500/20 text-teal-400 border border-teal-500/30 flex items-center justify-center font-black text-2xl mb-4 shadow-inner">
              5%
            </div>
            <h2 className="font-extrabold text-xl text-white">Gram Panchayat Fund</h2>
            <p className="text-xs sm:text-sm text-stone-400 mt-2 leading-relaxed">
              Every stay automatically channels 5% into the local village development fund for eco-trails, solar lighting, and mountain sanitation.
            </p>
          </motion.div>

          <motion.div
            whileHover={{ y: -4, rotate: -0.5 }}
            className="bg-stone-900/80 backdrop-blur-xl p-8 rounded-3xl border border-white/10 shadow-xl relative overflow-hidden group hover:border-blue-500/50 transition-all"
          >
            <div className="w-14 h-14 rounded-2xl bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-black text-2xl mb-4 shadow-inner">
              5%
            </div>
            <h2 className="font-extrabold text-xl text-white">Transparent Tech Fee</h2>
            <p className="text-xs sm:text-sm text-stone-400 mt-2 leading-relaxed">
              Just 5% platform fee to maintain tourist crowd redistribution servers, SOS emergency telemetry, and multilingual host tooling.
            </p>
          </motion.div>
        </div>

        {/* Feature Highlights Grid */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-extrabold text-white tracking-tight">Ecosystem Navigation</h2>
              <p className="text-xs sm:text-sm text-stone-400 mt-0.5">Everything needed to manage your rural hospitality operations</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <Link
              href="/host/onboarding"
              className="p-6 rounded-3xl bg-stone-900/70 border border-white/10 hover:border-amber-500/50 transition-all shadow-xl group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 group-hover:scale-110 transition-transform">
                  <Mic className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Voice Onboarding</h3>
              </div>
              <p className="text-xs text-stone-400 leading-relaxed">
                Speak naturally about your home, organic farm, and food. Our AI draft assistant formats your listing without guessing prices.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs font-bold text-amber-400">
                <span>Start Listing</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            <Link
              href="/host/dashboard"
              className="p-6 rounded-3xl bg-stone-900/70 border border-white/10 hover:border-emerald-500/50 transition-all shadow-xl group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition-transform">
                  <Home className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Host Dashboard</h3>
              </div>
              <p className="text-xs text-stone-400 leading-relaxed">
                Real-time dashboard showing active bookings, guest arrivals, verification status, and quick listing management.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                <span>Open Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            <Link
              href="/host/earnings"
              className="p-6 rounded-3xl bg-stone-900/70 border border-white/10 hover:border-blue-500/50 transition-all shadow-xl group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 group-hover:scale-110 transition-transform">
                  <TrendingUp className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Earnings & Community Fund</h3>
              </div>
              <p className="text-xs text-stone-400 leading-relaxed">
                Deterministic fee calculations: Gross value, 5% platform fee, 5% village contribution, and net payouts.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs font-bold text-blue-400">
                <span>View Earnings</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            <Link
              href="/host/listings"
              className="p-6 rounded-3xl bg-stone-900/70 border border-white/10 hover:border-purple-500/50 transition-all shadow-xl group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 group-hover:scale-110 transition-transform">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Panchayat Verification</h3>
              </div>
              <p className="text-xs text-stone-400 leading-relaxed">
                Track your verification lifecycle: SUBMITTED → UNDER REVIEW → VERIFIED → PUBLISHED with audit trail notes.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs font-bold text-purple-400">
                <span>Check Status</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            <Link
              href="/host/availability"
              className="p-6 rounded-3xl bg-stone-900/70 border border-white/10 hover:border-rose-500/50 transition-all shadow-xl group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 group-hover:scale-110 transition-transform">
                  <Calendar className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Availability Calendar</h3>
              </div>
              <p className="text-xs text-stone-400 leading-relaxed">
                Toggle room availability across 30 days and configure seasonal price adjustments for peak orchid bloom windows.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs font-bold text-rose-400">
                <span>Manage Calendar</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            <Link
              href="/host/bookings"
              className="p-6 rounded-3xl bg-stone-900/70 border border-white/10 hover:border-amber-500/50 transition-all shadow-xl group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 group-hover:scale-110 transition-transform">
                  <Users className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Guest Reservations</h3>
              </div>
              <p className="text-xs text-stone-400 leading-relaxed">
                View incoming travelers, check-in dates, emergency contacts, and digital verified QR travel passes.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs font-bold text-amber-400">
                <span>View Bookings</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
