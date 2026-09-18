'use client';

import React, { useState } from 'react';
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
  PhoneCall,
  Leaf,
  Sparkles,
  Tag,
  Info,
  Gift
} from 'lucide-react';
import { formatINR } from '@/lib/utils';

export default function TouristDashboardPage() {
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleUseCredits = () => {
    setToastMessage('30 Green Credits will be applied to your next eligible booking.');
    setTimeout(() => {
      setToastMessage(null);
    }, 4500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 relative">
      {/* Small toast / alert notification */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 max-w-md animate-in fade-in slide-in-from-top-3 duration-300">
          <div className="bg-emerald-900/95 text-emerald-100 border border-emerald-500/50 shadow-[0_20px_55px_rgba(23,23,20,0.10)] rounded-[20px] p-4 flex items-start gap-3 backdrop-blur-md">
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 shrink-0 mt-0.5">
              <Leaf className="w-5 h-5 animate-pulse" />
            </div>
            <div className="flex-1">
              <p className="font-bold text-sm text-white flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                Credits Reserved
              </p>
              <p className="text-xs text-emerald-200 mt-1 leading-relaxed">
                {toastMessage}
              </p>
            </div>
            <button
              onClick={() => setToastMessage(null)}
              className="text-emerald-400 hover:text-white text-xs font-mono ml-2 px-1"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-amber-600 via-rose-600 to-amber-700 rounded-[24px] p-6 sm:p-8 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-[0_12px_40px_rgba(23,23,20,0.06)]">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-[20px] bg-[#FCFAF6]/20 backdrop-blur-md flex items-center justify-center text-white border border-white/30 text-2xl font-black shadow-inner">
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
            className="px-4 py-2.5 rounded-xl bg-[#FCFAF6] text-slate-900 text-xs font-bold hover:bg-slate-100 transition-colors shadow-sm flex items-center gap-1.5"
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
        <div className="lg:col-span-2 bg-[#FCFAF6] dark:bg-slate-900 rounded-[20px] p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
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
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 text-white dark:bg-[#FCFAF6] dark:text-slate-900 text-xs font-bold hover:bg-amber-600 dark:hover:bg-amber-500 dark:hover:text-white transition-colors"
            >
              <span>Open Trip Companion</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Green Credits Card (Modern Sustainable-Tourism In-Platform Reward Card) */}
        <div className="bg-gradient-to-br from-emerald-950 via-slate-900 to-emerald-900/90 text-white rounded-[20px] p-6 border border-emerald-500/30 shadow-lg relative overflow-hidden flex flex-col justify-between group hover:border-emerald-400/50 transition-all duration-300">
          {/* Subtle Ambient Background Glow */}
          <div className="absolute -top-12 -right-12 w-36 h-36 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-12 -left-12 w-32 h-32 bg-teal-500/10 rounded-full blur-2xl pointer-events-none" />

          <div className="relative z-10 space-y-4">
            {/* Card Header */}
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/20 shadow-sm">
                  <Leaf className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-extrabold text-sm tracking-tight text-white flex items-center gap-1.5">
                    Green Credits
                  </h3>
                  <p className="text-[10px] text-emerald-400/90 font-medium">In-Platform Sustainable Rewards</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-[10px] font-bold text-emerald-300 font-mono flex items-center gap-1">
                <Tag className="w-2.5 h-2.5" />
                Discount Ready
              </span>
            </div>

            {/* Credit Balance Display */}
            <div className="flex items-baseline justify-between pt-1">
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-black font-mono tracking-tight text-emerald-300 drop-shadow-sm">
                    30
                  </span>
                  <span className="text-xs font-semibold text-emerald-100/80">Available Credits</span>
                </div>
                <p className="text-[11px] text-slate-300 mt-1 italic leading-tight">
                  Earned for choosing sustainable travel options
                </p>
              </div>
            </div>

            {/* Progress / Reward Indicator */}
            <div className="bg-black/30 backdrop-blur-sm rounded-xl p-2.5 border border-emerald-500/20 space-y-1.5">
              <div className="flex justify-between items-center text-[10px] font-mono">
                <span className="text-emerald-300 font-semibold flex items-center gap-1">
                  🌿 30 Credits
                </span>
                <span className="text-emerald-400 font-bold">Next booking discount available</span>
              </div>
              <div className="w-full bg-emerald-950/80 h-2 rounded-full overflow-hidden p-0.5 border border-emerald-500/30">
                <div className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full w-4/5 animate-pulse" />
              </div>
            </div>

            {/* Earning Breakdown */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400/90 font-mono block">
                Earning Breakdown
              </span>
              <div className="space-y-1 text-xs">
                <div className="flex items-center justify-between py-1 px-2 rounded-lg bg-[#FCFAF6]/5 border border-white/5">
                  <span className="text-slate-300 text-[11px]">Chose a low-pressure destination</span>
                  <span className="font-mono font-bold text-emerald-400 text-[11px]">+15</span>
                </div>
                <div className="flex items-center justify-between py-1 px-2 rounded-lg bg-[#FCFAF6]/5 border border-white/5">
                  <span className="text-slate-300 text-[11px]">Selected an off-peak travel period</span>
                  <span className="font-mono font-bold text-emerald-400 text-[11px]">+10</span>
                </div>
                <div className="flex items-center justify-between py-1 px-2 rounded-lg bg-[#FCFAF6]/5 border border-white/5">
                  <span className="text-slate-300 text-[11px]">Chose a verified rural stay</span>
                  <span className="font-mono font-bold text-emerald-400 text-[11px]">+5</span>
                </div>
                <div className="flex items-center justify-between pt-1 px-2 font-mono text-[11px] border-t border-white/10 text-emerald-200">
                  <span className="font-bold">TOTAL EARNED</span>
                  <span className="font-black text-emerald-300">30 Green Credits</span>
                </div>
              </div>
            </div>

            {/* Explanatory Callout */}
            <div className="text-[11px] text-emerald-100/90 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-2.5 leading-relaxed">
              <p className="font-medium">
                Your sustainable choices earn Green Credits. Use your Green Credits as a discount on your next eligible Yatri Setu booking.
              </p>
            </div>
          </div>

          {/* Action Button & Disclaimer */}
          <div className="relative z-10 pt-4 mt-2 border-t border-white/10 space-y-2">
            <button
              onClick={handleUseCredits}
              type="button"
              className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-extrabold text-xs shadow-md hover:shadow-emerald-500/25 active:scale-[0.98] transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span>Use on Next Booking</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <p className="text-[10px] text-center text-slate-400 font-mono">
              Mock reward system • Terms may apply
            </p>
          </div>
        </div>
      </div>

      {/* Safety Readiness Scorecard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-3 bg-[#FCFAF6] dark:bg-slate-900 rounded-[20px] p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
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

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Verified Homestay Host Contact', status: true },
                { label: 'Offline Pass Saved on Device', status: true },
                { label: 'GPS Geofence Tracking Armed', status: true },
                { label: 'Emergency Responder Hub Linked', status: true },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
                  <span className="text-slate-600 dark:text-slate-300">{item.label}</span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 ml-2" />
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

          <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end">
            <Link
              href="/safety/sos"
              className="py-2.5 px-5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/30 text-xs font-bold transition-colors inline-flex items-center gap-2"
            >
              <span>Review Emergency SOS Protocol</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
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
              className="bg-[#FCFAF6] dark:bg-slate-900 rounded-[20px] p-5 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between"
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
