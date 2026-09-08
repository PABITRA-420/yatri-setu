'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Destination, CrowdResponse } from '@/types';
import { fetchDestinationDetails, fetchDestinationCrowd } from '@/lib/api';
import { CrowdGauge } from '@/components/CrowdGauge';
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
  Home
} from 'lucide-react';

export default function DestinationDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = typeof params?.id === 'string' ? params.id : 'darjeeling';

  const [destination, setDestination] = useState<Destination | null>(null);
  const [crowd, setCrowd] = useState<CrowdResponse | null>(null);
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

  if (loading || !destination) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center animate-pulse">
        <div className="h-10 w-64 bg-slate-200 dark:bg-slate-800 rounded-xl mx-auto mb-4" />
        <div className="h-6 w-96 bg-slate-200 dark:bg-slate-800 rounded-lg mx-auto" />
      </div>
    );
  }

  const isOvercrowded = crowd && crowd.crowd_score > 75;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Overcrowding Alert Banner if Very High */}
      {isOvercrowded && (
        <div className="bg-rose-500/10 border-2 border-rose-500/30 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-rose-500 text-white shrink-0 mt-0.5">
              <Flame className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-extrabold text-sm sm:text-base text-rose-700 dark:text-rose-400">
                  Critical Congestion Warning for {destination.name} (Crowd: {crowd?.crowd_score}/100)
                </h3>
                <span className="text-[10px] font-bold uppercase bg-rose-600 text-white px-2 py-0.5 rounded">
                  SIH Flow Active
                </span>
              </div>
              <p className="text-xs text-rose-600/90 dark:text-rose-400/90 mt-0.5">
                Hotel saturation exceeds 91% and Hill Cart Road is backed up by 45+ mins. 
                Yatri Setu recommends shifting your booking to <strong>Kalimpong (87% Similarity)</strong>.
              </p>
            </div>
          </div>

          <Link
            href={`/destinations/${destination.id}/alternatives`}
            className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-md shadow-rose-600/20 active:scale-95 transition-all flex items-center gap-1.5 whitespace-nowrap"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>View Serene Alternatives</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {/* Hero Visual Section */}
      <div className="relative rounded-3xl overflow-hidden shadow-xl min-h-[380px] sm:min-h-[460px] flex items-end">
        <img
          src={destination.hero_image}
          alt={destination.name}
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/95 via-slate-950/40 to-transparent" />

        {/* Hero Bottom Overlay */}
        <div className="relative z-10 p-6 sm:p-10 w-full flex flex-col md:flex-row md:items-end justify-between gap-6 text-white">
          <div className="max-w-2xl space-y-2">
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

            <h1 className="text-3xl sm:text-5xl font-black tracking-tight">{destination.name}</h1>
            <p className="text-sm sm:text-base text-slate-200 line-clamp-2">
              {destination.tagline}
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <Link
              href={`/destinations/${destination.id}/crowd`}
              className="px-5 py-3 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-lg shadow-amber-600/30 flex items-center gap-2 transition-all active:scale-95"
            >
              <Flame className="w-4 h-4" />
              <span>Full Crowd Intelligence</span>
            </Link>

            <Link
              href={`/destinations/${destination.id}/alternatives`}
              className="px-5 py-3 rounded-xl bg-white/20 hover:bg-white/30 text-white backdrop-blur-md text-xs font-bold flex items-center gap-2 transition-all"
            >
              <Sparkles className="w-4 h-4" />
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
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Destination Overview
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {destination.description}
            </p>

            {/* Highlights List */}
            <div className="pt-2 space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Key Sights & Heritage
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {destination.highlights.map((highlight, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                    <span>{highlight}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Attractions */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Key Attractions & Real-time Density
            </h2>

            <div className="space-y-4">
              {destination.attractions.map((attraction) => (
                <div
                  key={attraction.id}
                  className="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row gap-4"
                >
                  <img
                    src={attraction.image_url}
                    alt={attraction.name}
                    className="w-full sm:w-36 h-28 rounded-xl object-cover"
                  />
                  <div className="flex-1 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <h4 className="font-extrabold text-base text-slate-900 dark:text-white">
                          {attraction.name}
                        </h4>
                        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                          attraction.crowd_density === 'High' ? 'bg-rose-500/10 text-rose-600' : 'bg-emerald-500/10 text-emerald-600'
                        }`}>
                          {attraction.crowd_density} Density
                        </span>
                      </div>
                      <span className="text-xs text-amber-600 font-semibold">{attraction.category}</span>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        {attraction.description}
                      </p>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        Best: {attraction.best_time}
                      </span>
                      <span>•</span>
                      <span>Duration: ~{attraction.visit_duration_hrs} hrs</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 4 Cols: Crowd Gauge Card & Fast Actions */}
        <div className="lg:col-span-4 space-y-6">
          {/* Live Crowd Card */}
          {crowd && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-4">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Live Footfall Evaluation
              </span>

              <CrowdGauge score={crowd.crowd_score} level={crowd.crowd_level} size="lg" />

              <div className="pt-4 border-t border-slate-100 dark:border-slate-800 text-left space-y-2 text-xs text-slate-500">
                <div className="flex justify-between">
                  <span>Peak Hours:</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{crowd.peak_visiting_hours}</span>
                </div>
                <div className="flex justify-between">
                  <span>Hotel Occupancy:</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{crowd.hotel_occupancy_rate}</span>
                </div>
                <div className="flex justify-between">
                  <span>Traffic Status:</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{crowd.live_traffic_status}</span>
                </div>
              </div>

              <Link
                href={`/destinations/${destination.id}/crowd`}
                className="w-full py-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30 text-xs font-bold block transition-colors"
              >
                Inspect Why It&apos;s Crowded →
              </Link>
            </div>
          )}

          {/* Quick Actions Card */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl p-6 shadow-md space-y-4">
            <h3 className="font-bold text-base">Plan Your Experience</h3>
            <p className="text-xs text-slate-300">
              Generate a crowd-avoiding itinerary or book authentic rural homestays directly.
            </p>

            <div className="space-y-2.5 pt-2">
              <Link
                href={`/itinerary?destination=${destination.id}`}
                className="w-full py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-colors shadow-sm"
              >
                <Calendar className="w-4 h-4" />
                <span>Create AI Itinerary</span>
              </Link>

              <Link
                href={`/homestays?destination_id=${destination.id}`}
                className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
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
