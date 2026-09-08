'use client';

import React from 'react';
import Link from 'next/link';
import { 
  User, 
  MapPin, 
  ShieldCheck, 
  Flame, 
  Calendar, 
  ArrowRight, 
  QrCode, 
  AlertTriangle,
  Heart,
  CheckCircle2,
  PhoneCall
} from 'lucide-react';
import { formatINR } from '@/lib/utils';

export default function TouristDashboardPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-amber-600 via-rose-600 to-amber-700 rounded-3xl p-6 sm:p-8 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white border border-white/30 text-2xl font-black shadow-inner">
            AS
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
                Namaste, Aarav Sharma
              </h1>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/90 text-[10px] font-bold uppercase tracking-wider">
                Verified Traveler
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-100 mt-1">
              Active Eco-Citizen • SIH 2026 Smart Tourist Companion
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/trips/demo-kalimpong"
            className="px-4 py-2.5 rounded-xl bg-white text-slate-900 text-xs font-bold hover:bg-slate-100 transition-colors shadow-sm flex items-center gap-1.5"
          >
            <QrCode className="w-4 h-4 text-amber-600" />
            <span>Digital Travel Pass</span>
          </Link>
          <Link
            href="/safety/sos"
            className="px-4 py-2.5 rounded-xl bg-rose-700 hover:bg-rose-800 text-white text-xs font-bold transition-colors flex items-center gap-1.5"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>SOS Safety</span>
          </Link>
        </div>
      </div>

      {/* Grid: Active Journey & Crowd Warning Ticker */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Journey Card */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Active Upcoming Journey
              </span>
              <span className="text-xs font-mono text-slate-400">
                Booking Ref: YS-BK-7492A
              </span>
            </div>

            <div className="mt-4 flex flex-col sm:flex-row gap-5">
              <img
                src="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80"
                alt="Pineview Orchid Retreat"
                className="w-full sm:w-44 h-36 rounded-xl object-cover"
              />
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center gap-1 text-xs text-amber-600 font-semibold">
                  <MapPin className="w-3.5 h-3.5" />
                  <span>Kalimpong, West Bengal (4,100 ft)</span>
                </div>
                <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">
                  Pineview Orchid Retreat & Homestay
                </h3>
                <p className="text-xs text-slate-500">
                  Host: Pemba & Choden Sherpa • 3 Nights (Oct 12 - Oct 15, 2026)
                </p>
                <div className="pt-2 flex flex-wrap gap-2">
                  <span className="text-[10px] font-bold bg-amber-500/10 text-amber-600 px-2 py-0.5 rounded border border-amber-500/20">
                    Crowd: Moderate (42/100)
                  </span>
                  <span className="text-[10px] font-bold bg-emerald-500/10 text-emerald-600 px-2 py-0.5 rounded border border-emerald-500/20">
                    10% Local Village Fund Included
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="text-xs text-slate-500 flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-amber-600" />
              <span>Itinerary: 3-Day Orchid & Monastery Immersion</span>
            </div>
            <Link
              href="/trips/demo-kalimpong"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 text-xs font-bold hover:bg-amber-600 dark:hover:bg-amber-500 dark:hover:text-white transition-colors"
            >
              <span>Open Trip Companion</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Safety Readiness Scorecard */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-xl bg-rose-500/10 text-rose-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                  Safety Readiness
                </h3>
                <span className="text-[10px] text-slate-400">95% Prepared</span>
              </div>
            </div>

            <div className="space-y-3">
              {[
                { label: 'Verified Homestay Host Contact', status: true },
                { label: 'Offline Pass Saved on Device', status: true },
                { label: 'GPS Geofence Tracking Armed', status: true },
                { label: 'Emergency Responder Hub Linked', status: true },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="text-slate-600 dark:text-slate-300">{item.label}</span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                </div>
              ))}
            </div>

            {/* Weather alert */}
            <div className="mt-5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-400">
              <div className="font-bold flex items-center gap-1 mb-0.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Regional Advisory</span>
              </div>
              Darjeeling Mall Road has critical congestion (88/100). Kalimpong ridge routes remain smooth and pleasant.
            </div>
          </div>

          <Link
            href="/safety/sos"
            className="mt-5 w-full py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/30 text-xs font-bold text-center block transition-colors"
          >
            Review Emergency SOS Protocol
          </Link>
        </div>
      </div>

      {/* Watchlist & Alternate Recommendations */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg text-slate-900 dark:text-white">
            Monitored Regional Destinations
          </h2>
          <Link href="/destinations" className="text-xs font-semibold text-amber-600 hover:underline">
            View All
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              name: 'Darjeeling',
              score: 88,
              level: 'VERY HIGH',
              status: 'Avoid or divert to Kalimpong',
              cost: 4800,
              badgeColor: 'bg-rose-500/10 text-rose-600 border-rose-500/30'
            },
            {
              name: 'Kalimpong',
              score: 42,
              level: 'MEDIUM',
              status: 'Optimal calm ridge retreat',
              cost: 2800,
              badgeColor: 'bg-amber-500/10 text-amber-600 border-amber-500/30'
            },
            {
              name: 'Lava / Neora',
              score: 24,
              level: 'LOW',
              status: 'Pristine forest tranquility',
              cost: 2100,
              badgeColor: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30'
            }
          ].map((dest) => (
            <div
              key={dest.name}
              className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-base text-slate-900 dark:text-white">
                    {dest.name}
                  </h4>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${dest.badgeColor}`}>
                    {dest.score}/100 {dest.level}
                  </span>
                </div>
                <p className="text-xs text-slate-500">{dest.status}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {formatINR(dest.cost)} / day
                </span>
                <Link
                  href={`/destinations/${dest.name.toLowerCase().split(' ')[0]}/crowd`}
                  className="text-amber-600 font-bold hover:underline flex items-center gap-0.5"
                >
                  <span>Check crowd</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
