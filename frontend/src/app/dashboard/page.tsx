'use client';

import React, { useState, useEffect, useCallback } from 'react';
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
  Gift,
  RefreshCw,
  Clock,
  Compass,
  Check
} from 'lucide-react';
import { formatINR, getCrowdBadgeStyle } from '@/lib/utils';
import { fetchTripDetails, fetchDestinations } from '@/lib/api';
import { TripDetailsResponse, DestinationSummary } from '@/types';

// Animated Count-Up KPI Component
function AnimatedNumber({ value, duration = 800 }: { value: number; duration?: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTimestamp: number | null = null;
    const startValue = 0;
    const endValue = value;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setDisplayValue(Math.round(startValue + (endValue - startValue) * ease));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    const animId = window.requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(animId);
  }, [value, duration]);

  return <>{displayValue}</>;
}

export default function TouristDashboardPage() {
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('Just now');
  
  // Dynamic API Data States
  const [trip, setTrip] = useState<TripDetailsResponse | null>(null);
  const [monitoredDestinations, setMonitoredDestinations] = useState<DestinationSummary[]>([]);
  
  // Interactive Green Credits State
  const [credits, setCredits] = useState<number>(30);
  const [creditsReserved, setCreditsReserved] = useState<boolean>(false);

  // Dynamic user profile
  const user = {
    name: 'Aarav Sharma',
    initials: 'AS',
    role: 'Verified Traveler',
    subtitle: 'Active Eco-Citizen • SIH 2026 Smart Tourist Companion'
  };

  const loadData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const [tripData, destinationsData] = await Promise.all([
        fetchTripDetails('demo-kalimpong'),
        fetchDestinations()
      ]);
      setTrip(tripData);
      setMonitoredDestinations(destinationsData.slice(0, 3));
      setLastUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
      if (isRefresh) setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleUseCredits = () => {
    if (creditsReserved) {
      setCreditsReserved(false);
      setToastMessage('Credits reservation cancelled. 30 Green Credits returned to wallet.');
    } else {
      setCreditsReserved(true);
      setToastMessage(`${credits} Green Credits applied! You will get an instant discount on your next booking.`);
    }
    setTimeout(() => {
      setToastMessage(null);
    }, 4500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 relative">
      {/* Toast Alert Notification */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 max-w-md animate-in fade-in slide-in-from-top-3 duration-300">
          <div className="bg-emerald-950/95 text-emerald-100 border border-emerald-500/50 shadow-2xl rounded-2xl p-4 flex items-start gap-3 backdrop-blur-md">
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 shrink-0 mt-0.5">
              <Leaf className="w-5 h-5 animate-pulse" />
            </div>
            <div className="flex-1">
              <p className="font-bold text-sm text-white flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                {creditsReserved ? 'Credits Reserved' : 'Wallet Updated'}
              </p>
              <p className="text-xs text-emerald-200 mt-1 leading-relaxed">
                {toastMessage}
              </p>
            </div>
            <button
              onClick={() => setToastMessage(null)}
              className="text-emerald-400 hover:text-white text-xs font-mono ml-2 px-1"
            >
              ?
            </button>
          </div>
        </div>
      )}

      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-amber-600 via-rose-600 to-amber-700 rounded-3xl p-6 sm:p-8 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-56 h-56 bg-white/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex items-center gap-4 relative z-10">
          <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white border border-white/30 text-2xl font-black shadow-inner shrink-0">
            {user.initials}
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
                Namaste, {user.name}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/90 text-[10px] font-bold uppercase tracking-wider">
                {user.role}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-100 mt-1">
              {user.subtitle}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <button
            onClick={() => loadData(true)}
            disabled={refreshing}
            className="px-3.5 py-2.5 rounded-xl bg-black/20 hover:bg-black/30 border border-white/20 text-white text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            title="Refresh dashboard data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span className="hidden md:inline">{refreshing ? 'Refreshing...' : `Synced ${lastUpdated}`}</span>
          </button>
          <Link
            href={`/trips/${trip?.trip_id || 'demo-kalimpong'}`}
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

      {/* Grid: Active Journey & Green Credits Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Journey Card */}
        <div className="lg:col-span-2 bg-white dark:bg-[#121824] rounded-2xl p-6 border border-slate-200/80 dark:border-white/10 shadow-sm flex flex-col justify-between relative overflow-hidden">
          {loading ? (
            <div className="space-y-4 animate-pulse">
              <div className="flex justify-between items-center pb-3 border-b border-slate-100 dark:border-white/5">
                <div className="h-4 w-40 bg-stone-300 dark:bg-stone-800 rounded" />
                <div className="h-4 w-28 bg-stone-300 dark:bg-stone-800 rounded" />
              </div>
              <div className="flex gap-5">
                <div className="w-44 h-36 bg-stone-300 dark:bg-stone-800 rounded-xl" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-32 bg-stone-300 dark:bg-stone-800 rounded" />
                  <div className="h-6 w-3/4 bg-stone-300 dark:bg-stone-800 rounded" />
                  <div className="h-4 w-1/2 bg-stone-300 dark:bg-stone-800 rounded" />
                </div>
              </div>
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  {trip?.status || 'Active Upcoming Journey'}
                </span>
                <span className="text-xs font-mono text-slate-400">
                  Pass Ref: {trip?.digital_pass_code || 'YS-PASS-7492A'}
                </span>
              </div>

              <div className="mt-4 flex flex-col sm:flex-row gap-5">
                <img
                  src="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80"
                  alt={trip?.homestay_name || 'Pineview Orchid Retreat'}
                  className="w-full sm:w-44 h-36 rounded-xl object-cover"
                />
                <div className="flex-1 space-y-1.5">
                  <div className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 font-semibold">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{trip?.check_in_location || 'Kalimpong, West Bengal'}</span>
                  </div>
                  <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">
                    {trip?.homestay_name || 'Pineview Orchid Retreat & Homestay'}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Support: {trip?.host_support_number || '+91 98320 87123'} • {trip?.dates || 'Oct 12 - Oct 15, 2026'}
                  </p>
                  <div className="pt-2 flex flex-wrap gap-2">
                    <span className="text-[10px] font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 px-2 py-0.5 rounded border border-amber-500/20">
                      Travelers: {trip?.travelers_count || 2} Pax
                    </span>
                    <span className="text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">
                      10% Local Village Fund Included
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-amber-600" />
              <span>Itinerary: 3-Day Orchid & Ridge Trail Immersion</span>
            </div>
            <Link
              href={`/trips/${trip?.trip_id || 'demo-kalimpong'}`}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 text-xs font-bold hover:bg-amber-600 dark:hover:bg-amber-500 dark:hover:text-white transition-colors"
            >
              <span>Open Trip Companion</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Green Credits Card */}
        <div className="bg-gradient-to-br from-emerald-950 via-slate-900 to-emerald-900/90 text-white rounded-2xl p-6 border border-emerald-500/30 shadow-lg relative overflow-hidden flex flex-col justify-between group hover:border-emerald-400/50 transition-all duration-300">
          <div className="absolute -top-12 -right-12 w-36 h-36 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-12 -left-12 w-32 h-32 bg-teal-500/10 rounded-full blur-2xl pointer-events-none" />

          <div className="relative z-10 space-y-4">
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
                {creditsReserved ? 'Discount Applied' : 'Discount Ready'}
              </span>
            </div>

            {/* Dynamic Animated Balance */}
            <div className="flex items-baseline justify-between pt-1">
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-black font-mono tracking-tight text-emerald-300 drop-shadow-sm">
                    <AnimatedNumber value={creditsReserved ? 0 : credits} />
                  </span>
                  <span className="text-xs font-semibold text-emerald-100/80">Available Credits</span>
                </div>
                <p className="text-[11px] text-slate-300 mt-1 italic leading-tight">
                  {creditsReserved ? '30 credits reserved for your next booking' : 'Earned for choosing sustainable travel options'}
                </p>
              </div>
            </div>

            {/* Dynamic Progress Bar */}
            <div className="bg-black/30 backdrop-blur-sm rounded-xl p-2.5 border border-emerald-500/20 space-y-1.5">
              <div className="flex justify-between items-center text-[10px] font-mono">
                <span className="text-emerald-300 font-semibold flex items-center gap-1">
                  ?? {creditsReserved ? 'Applied to next stay' : `${credits} / 50 Next Tier`}
                </span>
                <span className="text-emerald-400 font-bold">
                  {creditsReserved ? '?300 discount active' : 'Next booking discount available'}
                </span>
              </div>
              <div className="w-full bg-emerald-950/80 h-2 rounded-full overflow-hidden p-0.5 border border-emerald-500/30">
                <div 
                  className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500" 
                  style={{ width: creditsReserved ? '100%' : '60%' }}
                />
              </div>
            </div>

            {/* Earning Breakdown */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400/90 font-mono block">
                Earning Breakdown
              </span>
              <div className="space-y-1 text-xs">
                <div className="flex items-center justify-between py-1 px-2 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-slate-300 text-[11px]">Chose a low-pressure destination</span>
                  <span className="font-mono font-bold text-emerald-400 text-[11px]">+15</span>
                </div>
                <div className="flex items-center justify-between py-1 px-2 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-slate-300 text-[11px]">Selected an off-peak travel period</span>
                  <span className="font-mono font-bold text-emerald-400 text-[11px]">+10</span>
                </div>
                <div className="flex items-center justify-between py-1 px-2 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-slate-300 text-[11px]">Chose a verified rural stay</span>
                  <span className="font-mono font-bold text-emerald-400 text-[11px]">+5</span>
                </div>
                <div className="flex items-center justify-between pt-1 px-2 font-mono text-[11px] border-t border-white/10 text-emerald-200">
                  <span className="font-bold">TOTAL EARNED</span>
                  <span className="font-black text-emerald-300">{credits} Green Credits</span>
                </div>
              </div>
            </div>

            <div className="text-[11px] text-emerald-100/90 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-2.5 leading-relaxed">
              <p className="font-medium">
                Your sustainable choices earn Green Credits. Use your Green Credits as a discount on your next eligible Yatri Setu booking.
              </p>
            </div>
          </div>

          <div className="relative z-10 pt-4 mt-2 border-t border-white/10 space-y-2">
            <button
              onClick={handleUseCredits}
              type="button"
              className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-extrabold text-xs shadow-md hover:shadow-emerald-500/25 active:scale-[0.98] transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span>{creditsReserved ? 'Cancel Credit Reservation' : 'Use on Next Booking'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <p className="text-[10px] text-center text-slate-400 font-mono">
              Dynamic reward state • Instant redemption
            </p>
          </div>
        </div>
      </div>

      {/* Safety Readiness Scorecard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-3 bg-white dark:bg-[#121824] rounded-2xl p-6 border border-slate-200/80 dark:border-white/10 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-xl bg-rose-500/10 text-rose-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                  Safety Readiness
                </h3>
                <span className="text-[10px] text-slate-400 font-mono">
                  <AnimatedNumber value={95} />% Prepared
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Verified Homestay Host Contact', status: true },
                { label: 'Offline Pass Saved on Device', status: true },
                { label: 'GPS Geofence Tracking Armed', status: trip?.emergency_pin_active ?? true },
                { label: 'Emergency Responder Hub Linked', status: true },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-white/5">
                  <span className="text-slate-600 dark:text-slate-300">{item.label}</span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 ml-2" />
                </div>
              ))}
            </div>

            {/* Dynamic Weather Alert */}
            <div className="mt-5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-400">
              <div className="font-bold flex items-center gap-1 mb-0.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Regional Advisory</span>
              </div>
              {trip?.weather_alert || 'Darjeeling Mall Road has critical congestion (88/100). Kalimpong ridge routes remain smooth and pleasant.'}
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-slate-100 dark:border-white/5 flex justify-end">
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

      {/* Monitored Regional Destinations / Watchlist */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="font-bold text-lg text-slate-900 dark:text-white">
              Monitored Regional Destinations
            </h2>
            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 font-mono font-semibold">
              Live Feed
            </span>
          </div>
          <Link href="/destinations" className="text-xs font-semibold text-amber-600 dark:text-amber-400 hover:underline">
            View All
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-36 bg-slate-200 dark:bg-[#121824] border border-white/5 rounded-2xl" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {monitoredDestinations.map((dest) => {
              const badge = getCrowdBadgeStyle(dest.crowd_level);
              return (
                <div
                  key={dest.id}
                  className="bg-white dark:bg-[#121824] rounded-2xl p-5 border border-slate-200/80 dark:border-white/10 shadow-sm flex flex-col justify-between hover:border-amber-500/30 transition-all duration-300"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-bold text-base text-slate-900 dark:text-white">
                        {dest.name}
                      </h4>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${badge.badge}`}>
                        <AnimatedNumber value={dest.crowd_score} />/100 {dest.crowd_level}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">
                      {dest.tagline || `${dest.region}, ${dest.state}`}
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-700 dark:text-slate-300 font-mono">
                      {formatINR(dest.avg_cost_per_day_inr)} / day
                    </span>
                    <Link
                      href={`/destinations/${dest.id}/crowd`}
                      className="text-amber-600 dark:text-amber-400 font-bold hover:underline flex items-center gap-0.5"
                    >
                      <span>Check crowd</span>
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
