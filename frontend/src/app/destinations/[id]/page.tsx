'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Destination, CrowdResponse, Homestay } from '@/types';
import { fetchDestinationDetails, fetchDestinationCrowd, fetchHomestays } from '@/lib/api';
import { CrowdGauge } from '@/components/CrowdGauge';
import { HomestayCard } from '@/components/HomestayCard';
import { EmptyState } from '@/components/EmptyState';
import { formatINR, getCrowdBadgeStyle } from '@/lib/utils';
import { 
  MapPin, 
  Flame, 
  Sparkles, 
  Calendar, 
  ArrowRight, 
  Clock, 
  Compass, 
  Mountain, 
  Thermometer, 
  CheckCircle2, 
  Home,
  ShieldCheck,
  ChevronRight,
  Wind
} from 'lucide-react';

export default function DestinationDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = typeof params?.id === 'string' ? params.id : 'darjeeling';

  const [destination, setDestination] = useState<Destination | null>(null);
  const [crowd, setCrowd] = useState<CrowdResponse | null>(null);
  const [homestays, setHomestays] = useState<Homestay[]>([]);
  const [homestaysLoading, setHomestaysLoading] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [destData, crowdData] = await Promise.all([
        fetchDestinationDetails(id),
        fetchDestinationCrowd(id)
      ]);
      setDestination(destData);
      setCrowd(crowdData);
      setLoading(false);
    }
    load();
  }, [id]);

  useEffect(() => {
    async function loadHomestays() {
      setHomestaysLoading(true);
      const data = await fetchHomestays(id);
      setHomestays(data);
      setHomestaysLoading(false);
    }
    loadHomestays();
  }, [id]);

  if (loading || !destination) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center animate-pulse">
        <div className="h-10 w-64 bg-stone-200 dark:bg-stone-800 rounded-2xl mx-auto mb-4" />
        <div className="h-6 w-96 bg-stone-200 dark:bg-stone-800 rounded-xl mx-auto" />
      </div>
    );
  }

  const isOvercrowded = crowd && crowd.crowd_score > 75;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Overcrowding Alert Banner if Critical */}
      {isOvercrowded && (
        <div className="bg-rose-50 dark:bg-rose-950/30 border border-rose-300 dark:border-rose-900/60 rounded-3xl p-6 sm:p-7 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5 shadow-xs">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-2xl bg-rose-700 text-white shrink-0 mt-0.5">
              <Flame className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h3 className="font-extrabold text-base sm:text-lg text-rose-900 dark:text-rose-300 tracking-tight">
                  Critical Congestion Warning for {destination.name} (Crowd: {crowd?.crowd_score}/100)
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-rose-700 text-white px-2.5 py-0.5 rounded-full">
                  SIH Flow Active
                </span>
              </div>
              <p className="text-xs sm:text-sm text-rose-800/90 dark:text-rose-300/80 mt-1 leading-relaxed">
                Hotel saturation exceeds 91% and Hill Cart Road is backed up by 45+ mins. 
                Yatri Setu recommends shifting your booking to <strong>Kalimpong (87% Similarity, 42% cost savings)</strong>.
              </p>
            </div>
          </div>

          <Link
            href={`/destinations/${destination.id}/alternatives`}
            className="px-5 py-3 rounded-2xl bg-rose-700 hover:bg-rose-800 text-white font-bold text-xs shadow-md active:scale-97 transition-all flex items-center gap-2 whitespace-nowrap self-stretch sm:self-auto justify-center"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>View Serene Alternatives</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {/* Hero Visual Section: Full Editorial Treatment */}
      <div className="relative rounded-[2.5rem] overflow-hidden shadow-2xl min-h-[420px] sm:min-h-[500px] flex items-end bg-stone-950">
        <img
          src={destination.hero_image}
          alt={destination.name}
          className="absolute inset-0 w-full h-full object-cover filter brightness-[0.85]"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-stone-950/95 via-stone-950/40 to-transparent" />

        {/* Hero Bottom Overlay */}
        <div className="relative z-10 p-8 sm:p-12 w-full flex flex-col md:flex-row md:items-end justify-between gap-6 text-white">
          <div className="max-w-2xl space-y-3">
            <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-amber-300">
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5" />
                {destination.region}, {destination.state}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Mountain className="w-3.5 h-3.5" />
                {destination.attributes.altitude_ft.toLocaleString()} ft elevation
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Thermometer className="w-3.5 h-3.5" />
                {destination.attributes.climate}
              </span>
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight">{destination.name}</h1>
            <p className="text-sm sm:text-base text-stone-200 line-clamp-2 leading-relaxed">
              {destination.tagline}
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <Link
              href={`/destinations/${destination.id}/crowd`}
              className="px-5 py-3.5 rounded-2xl bg-amber-700 hover:bg-amber-800 text-white text-xs font-bold shadow-lg flex items-center gap-2 transition-all active:scale-97"
            >
              <Flame className="w-4 h-4" />
              <span>Full Crowd Intelligence</span>
            </Link>

            <Link
              href={`/destinations/${destination.id}/alternatives`}
              className="glass-pill px-5 py-3.5 rounded-2xl text-white text-xs font-bold flex items-center gap-2 transition-all hover:bg-white/30"
            >
              <Sparkles className="w-4 h-4 text-amber-300" />
              <span>Alternative Advisor</span>
            </Link>
          </div>
        </div>
      </div>


      {/* Main Grid: Details & Side Gauge */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left 8 Cols: Overview, Highlights, Attractions */}
        <div className="lg:col-span-8 space-y-8">
          {/* Overview */}
          <div className="bg-white dark:bg-[#121824] rounded-3xl p-7 sm:p-8 border border-stone-200/80 dark:border-white/10 shadow-xs space-y-4">
            <h2 className="text-xl font-extrabold text-stone-950 dark:text-white tracking-tight">
              Destination Overview
            </h2>
            <p className="text-sm text-stone-600 dark:text-stone-300 leading-relaxed">
              {destination.description}
            </p>

            {/* Highlights List */}
            <div className="pt-3 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-stone-400">
                Key Sights & Heritage Highlights
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {destination.highlights.map((highlight, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 text-xs text-stone-700 dark:text-stone-300 bg-stone-50 dark:bg-stone-900/40 p-2.5 rounded-xl border border-stone-200/60 dark:border-white/5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                    <span>{highlight}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Attractions */}
          <div className="space-y-4">
            <h2 className="text-xl font-extrabold text-stone-950 dark:text-white tracking-tight">
              Key Attractions & Real-time Footfall
            </h2>

            <div className="space-y-4">
              {destination.attractions.map((attraction) => (
                <div
                  key={attraction.id}
                  className="editorial-card bg-white dark:bg-[#121824] rounded-3xl p-5 border border-stone-200/80 dark:border-white/10 shadow-xs flex flex-col sm:flex-row gap-5"
                >
                  <img
                    src={attraction.image_url}
                    alt={attraction.name}
                    className="w-full sm:w-44 h-32 rounded-2xl object-cover"
                    loading="lazy"
                  />
                  <div className="flex-1 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <h4 className="font-extrabold text-base text-stone-950 dark:text-white tracking-tight">
                          {attraction.name}
                        </h4>
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                          attraction.crowd_density === 'High' ? 'bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-900/60' : 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-900/60'
                        }`}>
                          {attraction.crowd_density} Density
                        </span>
                      </div>
                      <span className="text-xs text-amber-700 dark:text-amber-400 font-semibold">{attraction.category}</span>
                      <p className="text-xs text-stone-500 dark:text-stone-400 mt-1.5 leading-relaxed">
                        {attraction.description}
                      </p>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-stone-400 pt-3 border-t border-stone-100 dark:border-white/5">
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-stone-400" />
                        Best Window: {attraction.best_time}
                      </span>
                      <span>•</span>
                      <span>Duration: ~{attraction.visit_duration_hrs} hrs</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Verified Homestays in This Destination */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-1.5 mb-1">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                    Panchayat Verified Community
                  </span>
                </div>
                <h2 className="text-xl font-extrabold text-stone-950 dark:text-white tracking-tight">
                  Verified Stays in {destination.name}
                </h2>
              </div>
              <Link
                href={`/homestays?destination_id=${destination.id}`}
                className="text-xs font-bold text-amber-700 dark:text-amber-400 hover:text-amber-800 flex items-center gap-1 transition-colors"
              >
                <span>View all</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {homestaysLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 animate-pulse">
                {[1, 2].map((i) => (
                  <div key={i} className="h-80 bg-stone-200 dark:bg-stone-800 rounded-3xl" />
                ))}
              </div>
            ) : homestays.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {homestays.slice(0, 4).map((hs) => (
                  <HomestayCard key={hs.id} homestay={hs} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right 4 Cols: Crowd Gauge Card & Fast Actions */}
        <div className="lg:col-span-4 space-y-6">
          {/* Live Crowd Card */}
          {crowd && (
            <div className="bg-white dark:bg-[#121824] rounded-3xl p-6 sm:p-7 border border-stone-200/80 dark:border-white/10 shadow-xs text-center space-y-5">
              <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider">
                Live Footfall Evaluation
              </span>

              <CrowdGauge score={crowd.crowd_score} level={crowd.crowd_level} size="lg" />

              <div className="pt-4 border-t border-stone-100 dark:border-white/5 text-left space-y-2.5 text-xs text-stone-500">
                <div className="flex justify-between">
                  <span>Peak Visiting:</span>
                  <span className="font-bold text-stone-800 dark:text-stone-200">{crowd.peak_visiting_hours}</span>
                </div>
                <div className="flex justify-between">
                  <span>Hotel Occupancy:</span>
                  <span className="font-bold text-stone-800 dark:text-stone-200 font-mono">{crowd.hotel_occupancy_rate}</span>
                </div>
                <div className="flex justify-between">
                  <span>Road Traffic:</span>
                  <span className="font-bold text-stone-800 dark:text-stone-200">{crowd.live_traffic_status}</span>
                </div>
              </div>

              <Link
                href={`/destinations/${destination.id}/crowd`}
                className="w-full py-3 rounded-2xl bg-stone-100 dark:bg-stone-800 hover:bg-stone-200/80 dark:hover:bg-stone-700 text-stone-900 dark:text-white text-xs font-bold block transition-colors"
              >
                Inspect 6-Factor Algorithm →
              </Link>
            </div>
          )}

          {/* Quick Actions Card */}
          <div className="bg-stone-950 text-white rounded-3xl p-7 shadow-xl border border-stone-800 space-y-4">
            <h3 className="font-extrabold text-lg tracking-tight">Plan Your Journey</h3>
            <p className="text-xs text-stone-300 leading-relaxed">
              Generate a crowd-avoiding itinerary or reserve authentic rural homestays directly with village panchayats.
            </p>

            <div className="space-y-3 pt-2">
              <Link
                href={`/itinerary?destination=${destination.id}`}
                className="w-full py-3 rounded-2xl bg-amber-400 hover:bg-amber-300 text-stone-950 text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-xs active:scale-97"
              >
                <Calendar className="w-4 h-4" />
                <span>Create Adaptive Itinerary</span>
              </Link>

              <Link
                href={`/homestays?destination_id=${destination.id}`}
                className="w-full py-3 rounded-2xl bg-white/10 hover:bg-white/15 text-white text-xs font-bold flex items-center justify-center gap-2 transition-colors border border-white/10"
              >
                <Home className="w-4 h-4" />
                <span>Verified Rural Homestays</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
