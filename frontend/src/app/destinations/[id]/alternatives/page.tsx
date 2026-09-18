'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { 
  AlternativesResponse, 
  DateAlternativesResponse, 
  DestinationDecisionResponse,
  RouteCalculationResponse
} from '@/types';
import { 
  fetchDestinationAlternatives, 
  fetchDateAlternatives, 
  fetchDestinationDecision,
  recordAlternativeAcceptance,
  fetchRouteEstimate
} from '@/lib/api';
import { AlternativeCard } from '@/components/AlternativeCard';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import dynamic from 'next/dynamic';

const YatriMap = dynamic(
  () => import('@/components/YatriMap').then((mod) => mod.YatriMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[460px] bg-stone-900/60 border border-stone-800 rounded-2xl flex flex-col items-center justify-center animate-pulse text-stone-400 gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin" />
        <span className="text-xs font-mono tracking-wider text-stone-400">
          INITIALIZING CORRIDOR MAP ENGINE...
        </span>
      </div>
    )
  }
);
import { getCrowdBadgeStyle, formatINR } from '@/lib/utils';
import { 
  Sparkles, 
  Flame, 
  ArrowLeft, 
  Calendar, 
  MapPin, 
  TrendingDown, 
  ShieldAlert, 
  ShieldCheck, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Compass, 
  Leaf, 
  HelpCircle,
  Split,
  ChevronRight,
  Navigation,
  CloudSun,
  Activity,
  Layers,
  Thermometer
} from 'lucide-react';

function AlternativesContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = typeof params?.id === 'string' ? params.id : 'darjeeling';

  const [activeTab, setActiveTab] = useState<'DESTINATION' | 'DATES'>('DESTINATION');
  const [altData, setAltData] = useState<AlternativesResponse | null>(null);
  const [dateData, setDateData] = useState<DateAlternativesResponse | null>(null);
  const [decision, setDecision] = useState<DestinationDecisionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Routing and Interactive Map state (Milestone 8A)
  const [selectedAltId, setSelectedAltId] = useState<string | null>(null);
  const [routeData, setRouteData] = useState<RouteCalculationResponse | null>(null);
  const [routeLoading, setRouteLoading] = useState(false);

  // Preferred dates state
  const [prefStartDate, setPrefStartDate] = useState(searchParams.get('start') || '2026-12-25');
  const [prefEndDate, setPrefEndDate] = useState(searchParams.get('end') || '2026-12-27');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [alts, dates, dec] = await Promise.all([
          fetchDestinationAlternatives(id).catch((err) => {
            console.warn('fetchDestinationAlternatives failed:', err);
            return null;
          }),
          fetchDateAlternatives(id, prefStartDate, prefEndDate).catch((err) => {
            console.warn('fetchDateAlternatives failed:', err);
            return null;
          }),
          fetchDestinationDecision(id, prefStartDate, prefEndDate).catch((err) => {
            console.warn('fetchDestinationDecision failed:', err);
            return null;
          })
        ]);
        setAltData(alts);
        setDateData(dates);
        setDecision(dec);
        const safeAlts = Array.isArray(alts?.alternatives) ? alts.alternatives : [];
        if (safeAlts.length > 0) {
          setSelectedAltId(safeAlts[0].id);
        }
      } catch (err: any) {
        console.error('AlternativesContent error:', err);
        setError(err?.message || 'Failed to load flow management data');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id, prefStartDate, prefEndDate]);

  // Fetch road route whenever selected alternative changes
  useEffect(() => {
    const targetAltId = selectedAltId;
    if (!targetAltId || !id) return;
    let isMounted = true;

    async function loadRoute(altId: string) {
      setRouteLoading(true);
      try {
        const data = await fetchRouteEstimate(id, altId);
        if (isMounted) {
          setRouteData(data);
        }
      } catch (err) {
        console.warn('Could not fetch route estimate:', err);
      } finally {
        if (isMounted) setRouteLoading(false);
      }
    }

    loadRoute(targetAltId);
    return () => { isMounted = false; };
  }, [id, selectedAltId]);

  const alternatives = Array.isArray(altData?.alternatives) ? altData.alternatives : [];
  const dateAlternatives = Array.isArray(dateData?.date_alternatives) ? dateData.date_alternatives : [];
  const originName = altData?.origin_destination_name || (typeof id === 'string' ? id.charAt(0).toUpperCase() + id.slice(1) : 'Darjeeling');
  const originCrowdScore = altData?.origin_crowd_score ?? 80;
  const isOvercrowded = originCrowdScore > 75;

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center animate-pulse">
        <div className="h-10 w-64 bg-stone-200 dark:bg-stone-800 rounded-2xl mx-auto mb-4" />
        <div className="h-6 w-96 bg-stone-200 dark:bg-stone-800 rounded-xl mx-auto" />
      </div>
    );
  }

  if (!altData && !dateData) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center space-y-4">
        <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto" />
        <h2 className="text-2xl font-bold text-stone-900 dark:text-white">
          Flow Advisory Unavailable
        </h2>
        <p className="text-sm text-stone-500 max-w-md mx-auto">
          {error || `Unable to load capacity telemetry and alternate destinations for '${id}'.`}
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="px-4 py-2 rounded-xl bg-stone-900 dark:bg-white text-white dark:text-stone-900 text-xs font-bold cursor-pointer"
          >
            Reload Page
          </button>
          <Link
            href="/destinations"
            className="px-4 py-2 rounded-xl bg-stone-200 dark:bg-stone-800 text-stone-800 dark:text-stone-200 text-xs font-bold"
          >
            View All Destinations
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Back Navigation */}
      <div>
        <Link
          href={`/destinations/${id}/crowd`}
          className="inline-flex items-center gap-2 text-xs font-bold text-stone-500 hover:text-stone-900 dark:hover:text-stone-200 mb-2 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to {originName} Crowd Intelligence</span>
        </Link>
      </div>

      {/* Primary Flow Management Hero Banner */}
      <div className={`rounded-[2.5rem] p-8 sm:p-12 text-white shadow-2xl border transition-all ${
        isOvercrowded 
          ? 'bg-stone-950 border-rose-900/40' 
          : 'bg-stone-950 border-stone-800'
      }`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
          <div className="space-y-4 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="px-3.5 py-1 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-extrabold uppercase tracking-wider flex items-center gap-1.5 font-mono">
                <Flame className="w-3.5 h-3.5 animate-pulse" />
                <span>Crowd Pressure: {originCrowdScore}/100</span>
              </span>
              <span className="px-3 py-1 rounded-full bg-white/10 text-[10px] font-bold uppercase tracking-widest text-stone-300">
                SIH 2026 Tourist Flow Engine
              </span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
              {isOvercrowded
                ? `Your destination (${originName}) is under critical congestion.`
                : `Active Flow Advisory for ${originName}`}
            </h1>

            <p className="text-xs sm:text-sm text-stone-300 leading-relaxed">
              Yatri Setu actively balances tourist distribution to safeguard Himalayan ecosystems. 
              Instead of competing with peak seasonal accommodation saturation and congested mountain access corridors, choose between 
              <strong className="text-white"> shifting to a serene destination</strong> or <strong className="text-white">adjusting your travel dates</strong>.
            </p>
          </div>

          {/* Recommended Flow Action Card */}
          <div className="glass-panel p-6 rounded-3xl text-center min-w-[280px] self-start lg:self-auto shrink-0 space-y-3">
            <span className="text-[10px] uppercase font-bold tracking-widest text-amber-700 dark:text-amber-400 block">
              Recommended Flow Action
            </span>
            <div className="px-4 py-2.5 rounded-2xl bg-amber-400 text-stone-950 font-extrabold text-xs tracking-wide shadow-xs">
              {decision?.recommended_action === 'CHANGE_DESTINATION' 
                ? 'A. CHANGE DESTINATION' 
                : decision?.recommended_action === 'CHANGE_DATES'
                ? 'B. CHANGE TRAVEL DATES'
                : 'KEEP DESTINATION'}
            </div>
            <p className="text-xs text-stone-600 dark:text-stone-300 leading-relaxed">
              {decision?.recommended_action === 'CHANGE_DESTINATION'
                ? 'Divert to neighboring ridges (lower crowd pressure & verified homestays)'
                : 'Shift to calm mid-week or post-holiday dates'}
            </p>
          </div>
        </div>
      </div>

      {/* Dual Pathway Switcher / Tabs */}
      <div className="flex items-center justify-center p-1.5 bg-stone-200/70 dark:bg-stone-900 rounded-2xl max-w-lg mx-auto border border-stone-300/80 dark:border-white/10">
        <button
          type="button"
          onClick={() => setActiveTab('DESTINATION')}
          className={`flex-1 py-3 px-5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'DESTINATION'
              ? 'bg-white dark:bg-[#121824] text-stone-950 dark:text-white shadow-xs'
              : 'text-stone-600 dark:text-stone-400 hover:text-stone-950 dark:hover:text-white'
          }`}
        >
          <Compass className="w-4 h-4 text-amber-600" />
          <span>Option A: Change Destination</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('DATES')}
          className={`flex-1 py-3 px-5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'DATES'
              ? 'bg-white dark:bg-[#121824] text-stone-950 dark:text-white shadow-xs'
              : 'text-stone-600 dark:text-stone-400 hover:text-stone-950 dark:hover:text-white'
          }`}
        >
          <Calendar className="w-4 h-4 text-amber-600" />
          <span>Option B: Change Dates</span>
        </button>
      </div>

      {/* ========================================================= */}
      {/* SECTION A: CHANGE DESTINATION (Geographical Decongestion) */}
      {/* ========================================================= */}
      {activeTab === 'DESTINATION' && (
        <div className="space-y-8 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
                Pathway A • Geographical Decongestion & Road Routing
              </span>
              <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                Interactive Circuit Route Advisor
              </h2>
            </div>
            <span className="text-xs text-slate-500">
              MapLibre + OpenFreeMap Liberty • Road travel intelligence
            </span>
          </div>

          {/* Interactive Circuit Map & Route Visualizer (Milestone 8A) */}
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-stone-500 dark:text-stone-400">
                  Select Alternative to Route:
                </span>
                {alternatives.map((alt) => (
                  <button
                    key={alt.id}
                    type="button"
                    onClick={() => setSelectedAltId(alt.id)}
                    className={`px-3 py-1 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                      selectedAltId === alt.id
                        ? 'bg-emerald-600 text-white shadow-sm ring-2 ring-emerald-400/40'
                        : 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-700'
                    }`}
                  >
                    <span>{alt.name}</span>
                    <span className="text-[10px] opacity-80 font-mono">({alt.crowd_score})</span>
                  </button>
                ))}
              </div>

              {routeLoading && (
                <span className="text-xs font-semibold text-amber-500 flex items-center gap-1.5 animate-pulse">
                  <Activity className="w-3.5 h-3.5 animate-spin" />
                  <span>Computing road corridor...</span>
                </span>
              )}
            </div>

            {/* MapLibre Canvas Container with Error Boundary */}
            <ErrorBoundary
              fallbackTitle="Interactive Map Unavailable"
              fallbackMessage="Map rendering is temporarily offline. All corridor distance metrics and alternative cards below are fully operational."
            >
              <YatriMap
                height="440px"
                originId={id}
                selectedDestinationId={selectedAltId || undefined}
                routeGeometry={routeData?.route_geometry}
                routeDistanceKm={routeData?.distance_km}
                routeDurationMin={routeData?.duration_minutes}
                isRoadDistance={routeData?.is_road_distance}
                provenanceLabel={routeData?.provenance_label}
                onSelectDestination={(destId) => setSelectedAltId(destId)}
              />
            </ErrorBoundary>

            {/* Corridor Routing Intelligence Panel */}
            {(() => {
              const activeAlt = alternatives.find((a) => a.id === selectedAltId) || alternatives[0];
              if (!activeAlt) return null;

              return (
                <div className="bg-white dark:bg-[#121824] rounded-3xl p-6 border border-stone-200/80 dark:border-white/10 shadow-xs space-y-5">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-stone-100 dark:border-white/5">
                    {/* Origin Station */}
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-2xl bg-rose-500/15 text-rose-500 flex items-center justify-center font-bold text-sm border border-rose-500/20">
                        <MapPin className="w-5 h-5" />
                      </div>
                      <div>
                        <span className="text-[10px] uppercase font-bold tracking-widest text-rose-600 dark:text-rose-400 block">
                          Origin Station
                        </span>
                        <h4 className="font-extrabold text-base text-stone-950 dark:text-white">
                          {originName}
                        </h4>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs font-bold text-rose-600 dark:text-rose-400">
                            Crowd: {originCrowdScore}/100
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Middle Route Stats */}
                    <div className="bg-stone-50 dark:bg-stone-900/60 px-5 py-3 rounded-2xl border border-stone-200/60 dark:border-white/5 text-center flex-1 max-w-md mx-auto">
                      <div className="flex items-center justify-center gap-2 mb-1">
                        <Navigation className="w-4 h-4 text-amber-500" />
                        <span className="text-xs font-extrabold text-stone-900 dark:text-white">
                          {routeData?.distance_km ?? activeAlt.distance_km} km
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-300 font-bold">
                          {routeData?.is_road_distance ? 'Road Route' : 'Approx. Geographic (Haversine)'}
                        </span>
                      </div>
                      <div className="text-[11px] text-stone-600 dark:text-stone-300 flex items-center justify-center gap-3">
                        <span>ETA: <strong>{routeData?.duration_minutes ? `~${routeData.duration_minutes} min` : 'Calculating...'}</strong></span>
                        <span>•</span>
                        <span>Mode: <strong>{routeData?.transit_mode || 'Shared Jeep'}</strong></span>
                      </div>
                      {routeData?.road_condition && (
                        <div className="text-[10px] text-stone-500 mt-1 italic">
                          {routeData.road_condition}
                        </div>
                      )}
                    </div>

                    {/* Recommended Alternative Station */}
                    <div className="flex items-center gap-3 text-right">
                      <div>
                        <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-600 dark:text-emerald-400 block">
                          Selected Alternative
                        </span>
                        <h4 className="font-extrabold text-base text-stone-950 dark:text-white">
                          {activeAlt.name}
                        </h4>
                        <div className="flex items-center justify-end gap-2 mt-0.5">
                          <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                            Crowd: {activeAlt.crowd_score}/100 ({activeAlt.crowd_level})
                          </span>
                        </div>
                      </div>
                      <div className="w-10 h-10 rounded-2xl bg-emerald-500/15 text-emerald-500 flex items-center justify-center font-bold text-sm border border-emerald-500/20">
                        <Sparkles className="w-5 h-5" />
                      </div>
                    </div>
                  </div>

                  {/* Telemetry Chips Row: Weather, Capacity, Traffic */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    {/* Weather */}
                    <div className="bg-stone-50 dark:bg-stone-900/40 p-3 rounded-2xl border border-stone-200/50 dark:border-white/5 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold text-stone-400 flex items-center gap-1">
                          <Thermometer className="w-3.5 h-3.5 text-amber-500" />
                          <span>Weather ({activeAlt.name})</span>
                        </span>
                        <span className="text-[9px] font-bold text-stone-400">
                          {activeAlt.weather?.provenance_label || 'REAL — OPENWEATHER'}
                        </span>
                      </div>
                      <div className="font-extrabold text-sm text-stone-900 dark:text-white">
                        {activeAlt.weather?.temperature !== undefined 
                          ? `${activeAlt.weather.temperature}°C • ${activeAlt.weather.condition}`
                          : (activeAlt.weather_summary || 'Mild Mountain Climate')}
                      </div>
                      {activeAlt.weather?.precipitation_chance !== undefined && (
                        <div className="text-[10px] text-stone-500">
                          Precipitation Chance: {activeAlt.weather.precipitation_chance}%
                        </div>
                      )}
                    </div>

                    {/* Capacity & Homestays */}
                    <div className="bg-stone-50 dark:bg-stone-900/40 p-3 rounded-2xl border border-stone-200/50 dark:border-white/5 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold text-stone-400 flex items-center gap-1">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                          <span>Capacity & Access</span>
                        </span>
                        <span className="text-[9px] font-bold text-emerald-500">
                          {activeAlt.access_status || 'OPEN'}
                        </span>
                      </div>
                      <div className="font-extrabold text-sm text-stone-900 dark:text-white">
                        Capacity: {activeAlt.capacity_status || 'HEALTHY'} ({activeAlt.available_capacity ? `${activeAlt.available_capacity}% Available` : 'Available'})
                      </div>
                      <div className="text-[10px] text-stone-500">
                        {activeAlt.homestay_availability || 'Verified panchayat homestays available'}
                      </div>
                    </div>

                    {/* Operational Provenance */}
                    <div className="bg-stone-50 dark:bg-stone-900/40 p-3 rounded-2xl border border-stone-200/50 dark:border-white/5 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold text-stone-400 flex items-center gap-1">
                          <Layers className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Data Provenance</span>
                        </span>
                        <span className="text-[9px] font-bold text-stone-400 font-mono">
                          M7C/M7D + M8A
                        </span>
                      </div>
                      <div className="font-bold text-[11px] text-stone-800 dark:text-stone-200 line-clamp-1">
                        {routeData?.provenance_label || 'DEMO MODE — SYNTHETIC DATA'}
                      </div>
                      <div className="text-[10px] text-stone-500">
                        Traffic: {routeData?.traffic_condition || 'Normal Corridor Flow'}
                      </div>
                    </div>
                  </div>

                  {/* Architecture Boundary Disclaimer */}
                  <p className="text-[11px] text-stone-500 dark:text-stone-400 italic pt-1 border-t border-stone-100 dark:border-white/5">
                    MapLibre/OpenFreeMap provides vector map visualization. Road travel metrics are calculated via routing-ready Himalayan network topology. Authoritative crowd & capacity decisions are managed deterministically by Yatri Setu M7C/M7D; map display does not decide recommended destinations.
                  </p>
                </div>
              );
            })()}
          </div>

          {/* Quick Summary Pill of #1 Recommendation */}
          {alternatives.length > 0 && (
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white font-bold flex items-center justify-center shrink-0">
                  #1
                </div>
                <div>
                  <span className="font-extrabold text-slate-900 dark:text-white text-sm">
                    {alternatives[0].name}
                  </span>
                  <span className="text-slate-500 ml-1.5">
                    ({alternatives[0].similarity_score}% Match • {alternatives[0].distance_km} km away • {alternatives[0].crowd_score} Crowd Score)
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-full bg-emerald-600 text-white font-bold text-[10px]">
                  {Math.abs(alternatives[0].cost_difference_percent)}% Cheaper
                </span>
                <Link
                  href={`/itinerary?destination=${alternatives[0].id}`}
                  onClick={() => {
                    recordAlternativeAcceptance(
                      id,
                      alternatives[0].id,
                      alternatives[0].similarity_score
                    );
                  }}
                  className="px-3.5 py-1.5 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-bold hover:bg-amber-600 transition-colors"
                >
                  Quick Select →
                </Link>
              </div>
            </div>
          )}

          {/* Alternative Cards with Active Selection for Map */}
          <div className="space-y-6">
            {alternatives.length > 0 ? (
              alternatives.map((alt) => (
                <AlternativeCard
                  key={alt.id}
                  alternative={alt}
                  originName={originName}
                  isSelected={alt.id === selectedAltId}
                  onSelectForMap={(altId) => setSelectedAltId(altId)}
                />
              ))
            ) : (
              <div className="p-8 rounded-3xl bg-stone-50 dark:bg-stone-900 border border-stone-200/80 dark:border-white/10 text-center space-y-3">
                <ShieldCheck className="w-8 h-8 text-emerald-500 mx-auto" />
                <h3 className="font-extrabold text-base text-stone-900 dark:text-white">
                  No Geographic Divergence Needed
                </h3>
                <p className="text-xs text-stone-500 max-w-md mx-auto">
                  {originName} is currently operating within comfortable carrying capacity with balanced visitor flow and available accommodations.
                </p>
              </div>
            )}
          </div>
        </div>
      )}


      {/* ==================================================== */}
      {/* SECTION B: CHANGE DATES (Temporal Decongestion)      */}
      {/* ==================================================== */}
      {activeTab === 'DATES' && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                Pathway B • Temporal Decongestion
              </span>
              <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                Calmer Seasonal Windows for {originName}
              </h2>
            </div>
            <div className="text-xs text-slate-500">
              Current Requested Dates: <strong className="text-slate-800 dark:text-slate-200">{dateData?.preferred_start_date || prefStartDate} to {dateData?.preferred_end_date || prefEndDate}</strong> ({dateData?.preferred_crowd_score ?? 80}/100 {dateData?.preferred_crowd_classification || 'MODERATE'})
            </div>
          </div>

          {/* Comparative Callout */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-5 text-xs text-amber-900 dark:text-amber-300 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="block text-sm mb-0.5">Stay at {originName} with up to 70% lower footfall:</strong>
              By adjusting your departure by just 1 to 2 weeks, you avoid peak holiday bottlenecks, secure up to 42% lower homestay rates, and enjoy unobstructed Kanchenjunga sunrises.
            </div>
          </div>

          {/* 3 Alternative Date Window Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {dateAlternatives.length > 0 ? (
              dateAlternatives.map((dateAlt, idx) => {
                const badge = getCrowdBadgeStyle(dateAlt.crowd_classification);
                return (
                  <div
                    key={idx}
                    className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-lg transition-all duration-300 flex flex-col justify-between group"
                  >
                    <div>
                      {/* Header with Window Label & Crowd Badge */}
                      <div className="flex items-center justify-between gap-2 mb-3">
                        <span className="text-xs font-extrabold text-amber-600 dark:text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                          Option {idx + 1}
                        </span>
                        <div className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border flex items-center gap-1 ${badge.bg} ${badge.border}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
                          <span>{dateAlt.crowd_score}/100 {dateAlt.crowd_classification}</span>
                        </div>
                      </div>

                      <h3 className="text-xl font-black text-slate-900 dark:text-white tracking-tight">
                        {dateAlt.window_label}
                      </h3>
                      <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                        {dateAlt.start_date} to {dateAlt.end_date}
                      </p>

                      {/* Metrics Grid */}
                      <div className="grid grid-cols-2 gap-2 my-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-center text-xs">
                        <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500/20">
                          <span className="text-[10px] uppercase font-bold text-emerald-600 block">
                            Crowd Reduction
                          </span>
                          <span className="font-black text-emerald-600 text-sm">
                            ↓ {dateAlt.crowd_reduction_percent}% Lower
                          </span>
                        </div>

                        <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">
                            Tariff Savings
                          </span>
                          <span className="font-black text-slate-900 dark:text-white text-sm">
                            {dateAlt.estimated_cost_change}
                          </span>
                        </div>
                      </div>

                      {/* Availability Score */}
                      <div className="mb-3 flex items-center justify-between text-xs text-slate-500">
                        <span>Room Availability:</span>
                        <strong className="text-emerald-600 dark:text-emerald-400">{dateAlt.availability_score}% Open</strong>
                      </div>

                      {/* Structured Reason */}
                      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-xl">
                        {dateAlt.reason}
                      </p>
                    </div>

                    {/* CTA */}
                    <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
                      <Link
                        href={`/itinerary?destination=${altData?.origin_destination_id || id}&start=${dateAlt.start_date}&end=${dateAlt.end_date}`}
                        className="w-full py-2.5 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-amber-600 dark:hover:bg-amber-500 dark:hover:text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-95"
                      >
                        <Calendar className="w-3.5 h-3.5" />
                        <span>Choose These Dates & Plan</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="col-span-full p-8 rounded-3xl bg-stone-50 dark:bg-stone-900 border border-stone-200/80 dark:border-white/10 text-center space-y-3">
                <Calendar className="w-8 h-8 text-amber-500 mx-auto" />
                <h3 className="font-extrabold text-base text-stone-900 dark:text-white">
                  No Date Window Shifting Needed
                </h3>
                <p className="text-xs text-stone-500 max-w-md mx-auto">
                  Your selected travel window does not conflict with peak holiday surges.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AlternativesPage() {
  return (
    <Suspense fallback={
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading flow management advisor...
      </div>
    }>
      <AlternativesContent />
    </Suspense>
  );
}
