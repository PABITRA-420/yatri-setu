'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Destination, CrowdResponse, Homestay, DestinationLiveConditions } from '@/types';
import { fetchDestinationDetails, fetchDestinationCrowd, fetchHomestays, fetchDestinationConditions } from '@/lib/api';
import { CrowdGauge } from '@/components/CrowdGauge';
import { HomestayCard } from '@/components/HomestayCard';
import { EmptyState } from '@/components/EmptyState';
import { YatriMap } from '@/components/YatriMap';
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
  Wind,
  CloudRain,
  Navigation,
  Eye,
  Car,
  AlertTriangle,
  Radio,
  Activity
} from 'lucide-react';

export default function DestinationDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = typeof params?.id === 'string' ? params.id : 'darjeeling';

  const [destination, setDestination] = useState<Destination | null>(null);
  const [crowd, setCrowd] = useState<CrowdResponse | null>(null);
  const [liveConditions, setLiveConditions] = useState<DestinationLiveConditions | null>(null);
  const [homestays, setHomestays] = useState<Homestay[]>([]);
  const [homestaysLoading, setHomestaysLoading] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [destData, crowdData, conditionsData] = await Promise.all([
        fetchDestinationDetails(id),
        fetchDestinationCrowd(id),
        fetchDestinationConditions(id).catch(() => null)
      ]);
      setDestination(destData);
      setCrowd(crowdData);
      setLiveConditions(conditionsData);
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
      {/* Mountain Corridor Access Disruption Warning (Milestone 7C) */}
      {liveConditions?.access_status === 'DISRUPTED' && (
        <div className="bg-red-500/10 border-2 border-red-500/60 rounded-3xl p-6 sm:p-7 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-2xl bg-red-600 text-white shrink-0 mt-0.5 animate-bounce">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h3 className="font-extrabold text-base sm:text-lg text-red-700 dark:text-red-400 tracking-tight">
                  Mountain Transit Disruption: Access to {destination.name} Impaired
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-red-600 text-white px-2.5 py-0.5 rounded-full">
                  CORRIDOR DISRUPTED
                </span>
              </div>
              <p className="text-xs sm:text-sm text-red-600/90 dark:text-red-300/90 mt-1 leading-relaxed">
                Primary arterial routes (such as {liveConditions.traffic?.primary_bottleneck_route || 'arterial mountain highways'}) report critical travel anomalies or active road blockage. Essential travel only.
              </p>
            </div>
          </div>
          <Link
            href={`/destinations/${destination.id}/alternatives`}
            className="px-5 py-3 rounded-2xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-md active:scale-97 transition-all flex items-center gap-2 whitespace-nowrap self-stretch sm:self-auto justify-center"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>Reroute to Open Destination</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

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
                Accommodation pressure: {crowd?.hotel_occupancy_rate || 'High (~90% seasonal baseline)'} • Mountain road status: {crowd?.live_traffic_status || 'Elevated transit delays'}. 
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

          {/* Live Conditions & Mountain Corridor Transit (Milestone 7C) */}
          {liveConditions && (
            <div className="bg-white dark:bg-[#121824] rounded-3xl p-7 sm:p-8 border border-stone-200/80 dark:border-white/10 shadow-xs space-y-6">
              {/* Header with Access Status and Provenance */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-100 dark:border-white/5">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-2xl shrink-0 ${
                    liveConditions.access_status === 'OPEN'
                      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                      : liveConditions.access_status === 'CAUTION'
                      ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                      : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
                  }`}>
                    <Activity className="w-5 h-5 animate-pulse" />
                  </div>
                  <div>
                    <h2 className="text-xl font-extrabold text-stone-950 dark:text-white tracking-tight flex items-center gap-2">
                      Live Mountain Conditions & Transit Corridors
                    </h2>
                    <p className="text-xs text-stone-500 dark:text-stone-400">
                      Real-time arterial pass delay, mountain weather & road accessibility
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                  {/* Distinct Access Status Badge */}
                  <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                    liveConditions.access_status === 'OPEN'
                      ? 'bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                      : liveConditions.access_status === 'CAUTION'
                      ? 'bg-amber-100 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                      : 'bg-rose-100 dark:bg-rose-950/50 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800'
                  }`}>
                    <span className={`w-2 h-2 rounded-full ${
                      liveConditions.access_status === 'OPEN' ? 'bg-emerald-500' : liveConditions.access_status === 'CAUTION' ? 'bg-amber-500' : 'bg-rose-500 animate-ping'
                    }`} />
                    ACCESS {liveConditions.access_status}
                  </span>

                  {/* Provenance Badge */}
                  <span className="text-[10px] font-mono font-semibold px-2.5 py-1 rounded-full bg-stone-100 dark:bg-stone-800/80 text-stone-600 dark:text-stone-300 border border-stone-200 dark:border-stone-700">
                    {liveConditions.provenance}
                  </span>
                </div>
              </div>

              {/* Grid: Live Weather & Corridor Traffic */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Weather Observation Block */}
                <div className="bg-stone-50 dark:bg-stone-900/40 rounded-2xl p-5 border border-stone-200/60 dark:border-white/5 space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-stone-400 flex items-center gap-1.5">
                      <Thermometer className="w-4 h-4 text-amber-500" />
                      Mountain Climate
                    </span>
                    <div className="flex items-center gap-1.5">
                      {liveConditions.weather.provider_mode === 'REAL' ? (
                        <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                          REAL (OpenWeather)
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                          DEMO (Synthetic)
                        </span>
                      )}
                      <span className="text-[10px] text-stone-400 font-mono">
                        {liveConditions.weather.cache_status === 'CACHED' ? 'Cached' : liveConditions.weather.cache_status === 'STALE' ? 'Stale' : 'Live'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-baseline gap-3">
                    <span className="text-3xl font-black text-stone-950 dark:text-white">
                      {liveConditions.weather.temperature_c.toFixed(1)}°C
                    </span>
                    <span className="text-xs text-stone-500 dark:text-stone-400">
                      High {liveConditions.weather.temp_max_c.toFixed(0)}°C / Low {liveConditions.weather.temp_min_c.toFixed(0)}°C
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-stone-700 dark:text-stone-300">
                    {liveConditions.weather.weather_condition}
                  </p>

                  {/* Weather Metrics Grid */}
                  <div className="grid grid-cols-3 gap-2 pt-1 text-center">
                    <div className="p-2 rounded-xl bg-white dark:bg-stone-800/60 border border-stone-200/40 dark:border-white/5">
                      <div className="flex items-center justify-center gap-1 text-[10px] text-stone-400 mb-0.5">
                        <CloudRain className="w-3 h-3 text-sky-500" />
                        <span>Rainfall</span>
                      </div>
                      <span className="text-xs font-bold text-stone-800 dark:text-stone-200">
                        {liveConditions.weather.precipitation_mm.toFixed(1)} mm
                      </span>
                    </div>

                    <div className="p-2 rounded-xl bg-white dark:bg-stone-800/60 border border-stone-200/40 dark:border-white/5">
                      <div className="flex items-center justify-center gap-1 text-[10px] text-stone-400 mb-0.5">
                        <Wind className="w-3 h-3 text-teal-500" />
                        <span>Wind</span>
                      </div>
                      <span className="text-xs font-bold text-stone-800 dark:text-stone-200">
                        {liveConditions.weather.wind_speed_kmh.toFixed(0)} km/h
                      </span>
                    </div>

                    <div className="p-2 rounded-xl bg-white dark:bg-stone-800/60 border border-stone-200/40 dark:border-white/5">
                      <div className="flex items-center justify-center gap-1 text-[10px] text-stone-400 mb-0.5">
                        <Eye className="w-3 h-3 text-indigo-500" />
                        <span>Visibility</span>
                      </div>
                      <span className="text-xs font-bold text-stone-800 dark:text-stone-200">
                        {liveConditions.weather.visibility_km.toFixed(1)} km
                      </span>
                    </div>
                  </div>

                  {liveConditions.weather.advisory && (
                    <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300 flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 shrink-0 text-amber-500 mt-0.5" />
                      <span>{liveConditions.weather.advisory}</span>
                    </div>
                  )}
                </div>

                {/* Arterial Corridor Traffic Block */}
                <div className="bg-stone-50 dark:bg-stone-900/40 rounded-2xl p-5 border border-stone-200/60 dark:border-white/5 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-stone-400 flex items-center gap-1.5">
                      <Car className="w-4 h-4 text-sky-500" />
                      Corridor Transit Status
                    </span>
                    <span className="text-[10px] text-stone-400 font-mono">
                      {liveConditions.condition_type}
                    </span>
                  </div>

                  <div className="flex items-baseline justify-between">
                    <div>
                      <span className="text-2xl font-black text-stone-950 dark:text-white">
                        {liveConditions.traffic.travel_time_anomaly_percent > 0
                          ? `+${liveConditions.traffic.travel_time_anomaly_percent.toFixed(0)}%`
                          : `${liveConditions.traffic.travel_time_anomaly_percent.toFixed(0)}%`}
                      </span>
                      <span className="text-xs text-stone-500 dark:text-stone-400 ml-1.5">
                        corridor delay
                      </span>
                    </div>
                    <span className={`text-xs font-bold uppercase px-2.5 py-0.5 rounded-full ${
                      liveConditions.access_status === 'OPEN'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300'
                        : liveConditions.access_status === 'CAUTION'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/40 dark:text-yellow-300'
                        : 'bg-rose-100 text-rose-800 dark:bg-rose-950/40 dark:text-rose-300'
                    }`}>
                      {liveConditions.access_status}
                    </span>
                  </div>

                  {/* Route List */}
                  <div className="space-y-2 pt-1">
                    {liveConditions.traffic.critical_routes.map((rt) => (
                      <div
                        key={rt.route_id}
                        className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-stone-800/60 border border-stone-200/40 dark:border-white/5 text-xs"
                      >
                        <div className="space-y-0.5">
                          <div className="font-semibold text-stone-800 dark:text-stone-200 flex items-center gap-1.5">
                            <Navigation className="w-3 h-3 text-stone-400" />
                            {rt.route_name}
                          </div>
                          <div className="text-[10px] text-stone-500 dark:text-stone-400">
                            {rt.current_travel_time_min} min (nominal: {rt.historical_travel_time_min} min)
                          </div>
                        </div>

                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          rt.road_status === 'CLEAR'
                            ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
                            : rt.road_status === 'SLOW'
                            ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400'
                            : 'bg-rose-500/10 text-rose-700 dark:text-rose-400'
                        }`}>
                          {rt.road_status}
                        </span>
                      </div>
                    ))}
                  </div>

                  {liveConditions.traffic.primary_bottleneck_route && (
                    <div className="text-[11px] text-stone-500 dark:text-stone-400">
                      Primary corridor bottleneck: <strong className="text-stone-800 dark:text-stone-200">{liveConditions.traffic.primary_bottleneck_route}</strong>
                    </div>
                  )}
                </div>
              </div>

              {/* Dynamic Pressure Recalculation Top Drivers */}
              <div className="pt-2 border-t border-stone-100 dark:border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-stone-800 dark:text-stone-200">
                    Recalculated Pressure: {liveConditions.pressure_score.toFixed(0)}/100 ({liveConditions.pressure_level})
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] text-stone-400 font-semibold uppercase tracking-wider">Top Drivers:</span>
                  {liveConditions.top_drivers.map((drv, i) => (
                    <span
                      key={i}
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 border border-stone-200 dark:border-stone-700"
                      title={drv.description}
                    >
                      {drv.signal} ({drv.impact > 0 ? `+${drv.impact.toFixed(0)}` : drv.impact.toFixed(0)} pts)
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Regional Circuit Map & Arterial Corridor Network (Milestone 8A) */}
          <div className="bg-white dark:bg-[#121824] rounded-3xl p-7 sm:p-8 border border-stone-200/80 dark:border-white/10 shadow-xs space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-100 dark:border-white/5">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 shrink-0">
                  <Compass className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-xl font-extrabold text-stone-950 dark:text-white tracking-tight flex items-center gap-2">
                    Regional Himalayan Circuit Map
                  </h2>
                  <p className="text-xs text-stone-500 dark:text-stone-400">
                    Live crowd, capacity & road accessibility across connected hill stations
                  </p>
                </div>
              </div>

              <Link
                href={`/destinations/${destination.id}/alternatives`}
                className="px-4 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-300 font-bold text-xs flex items-center gap-1.5 transition-colors border border-amber-500/20 self-start sm:self-auto"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span>Open Route Advisor</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <YatriMap
              height="400px"
              originId={destination.id}
              onSelectDestination={(destId) => {
                if (destId !== destination.id) {
                  router.push(`/destinations/${destId}`);
                }
              }}
            />

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-stone-500 dark:text-stone-400 pt-1">
              <span>Click any destination pin to inspect details or explore alternative routes.</span>
              <span className="font-mono text-[10px] text-stone-400">Style: OpenFreeMap Liberty • Engine: MapLibre GL JS</span>
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
                href={`/homestays?destination=${destination.id}`}
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
                href={`/homestays?destination=${destination.id}`}
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
