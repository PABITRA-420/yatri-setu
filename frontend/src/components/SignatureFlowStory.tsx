'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  AlertTriangle,
  Sparkles,
  Check,
  X,
  Activity,
  Compass,
  Leaf,
  TrendingDown,
  Shield,
  MapPin,
  Clock,
  IndianRupee,
  Users,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { fetchDestinations } from '@/lib/api';

/* ─────────────────────────────── Animated Counter Hook ─────────────────────────────── */
interface CountUpOptions {
  target: number;
  duration?: number;
  delay?: number;
  decimals?: number;
  useGrouping?: boolean;
  startTrigger: boolean;
}

function formatNumber(num: number, decimals: number, useGrouping: boolean): string {
  if (decimals > 0) {
    return num.toFixed(decimals);
  }
  const rounded = Math.round(num);
  return useGrouping ? rounded.toLocaleString('en-IN') : rounded.toString();
}

function useCountUp({
  target,
  duration = 1600,
  delay = 0,
  decimals = 0,
  useGrouping = false,
  startTrigger,
}: CountUpOptions): string {
  const initialValue = decimals > 0 ? (0).toFixed(decimals) : '0';
  const finalValue = formatNumber(target, decimals, useGrouping);
  const [displayValue, setDisplayValue] = useState<string>(initialValue);
  const startedRef = useRef(false);
  const prevTargetRef = useRef(target);

  useEffect(() => {
    if (startedRef.current && prevTargetRef.current !== target) {
      prevTargetRef.current = target;
      setDisplayValue(finalValue);
    }
  }, [target, finalValue]);

  useEffect(() => {
    if (!startTrigger || startedRef.current) return;
    startedRef.current = true;

    // Respect prefers-reduced-motion
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion || target === 0) {
      setDisplayValue(finalValue);
      return;
    }

    let animFrameId: number;
    let startTime: number | null = null;

    // Premium exponential ease-out: rapid surge, smooth subtle deceleration
    const easeOutExpo = (t: number): number =>
      t === 1 ? 1 : 1 - Math.pow(2, -10 * t);

    const step = (currentTime: number) => {
      if (startTime === null) startTime = currentTime;
      const elapsed = currentTime - startTime;

      if (elapsed < delay) {
        animFrameId = requestAnimationFrame(step);
        return;
      }

      const progress = Math.min((elapsed - delay) / duration, 1);
      const eased = easeOutExpo(progress);
      const current = eased * target;

      if (progress < 1) {
        setDisplayValue(formatNumber(current, decimals, useGrouping));
        animFrameId = requestAnimationFrame(step);
      } else {
        setDisplayValue(finalValue);
      }
    };

    animFrameId = requestAnimationFrame(step);

    return () => {
      if (animFrameId) cancelAnimationFrame(animFrameId);
    };
  }, [startTrigger, target, duration, delay, decimals, useGrouping, finalValue]);

  return displayValue;
}

/* ─────────────────────────────── Component ─────────────────────────────── */
export function SignatureFlowStory() {
  const sectionRef = useRef<HTMLElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [statsTriggered, setStatsTriggered] = useState(false);

  // Section entrance transition
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  // One-time 20-30% scroll trigger for statistics numbers
  useEffect(() => {
    if (statsTriggered) return;
    const el = statsRef.current;
    if (!el) return;

    if (typeof IntersectionObserver === 'undefined') {
      setStatsTriggered(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry && (entry.isIntersecting || entry.intersectionRatio >= 0.25)) {
          setStatsTriggered(true);
          observer.disconnect();
        }
      },
      { threshold: 0.25 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [statsTriggered]);

  // Live metrics state with graceful default fallbacks
  const [metrics, setMetrics] = useState({
    darjCrowd: 88,
    darjTariff: 4800,
    darjQueue: 2.5,
    kalCrowd: 42,
    kalTariff: 2800,
    kalWait: 0
  });

  // Fetch real telemetry on mount to update stats dynamically
  useEffect(() => {
    let isMounted = true;
    async function loadStoryTelemetry() {
      try {
        const dests = await fetchDestinations();
        if (!isMounted || !dests || dests.length === 0) return;

        const darj = dests.find(d => d.id.toLowerCase() === 'darjeeling');
        const kal = dests.find(d => d.id.toLowerCase() === 'kalimpong');

        setMetrics(prev => ({
          ...prev,
          darjCrowd: darj?.crowd_score ?? prev.darjCrowd,
          darjTariff: darj?.avg_cost_per_day_inr ?? prev.darjTariff,
          kalCrowd: kal?.crowd_score ?? prev.kalCrowd,
          kalTariff: kal?.avg_cost_per_day_inr ?? prev.kalTariff
        }));
      } catch (err) {
        console.warn('SignatureFlowStory live telemetry fallback active:', err);
      }
    }

    loadStoryTelemetry();
    return () => {
      isMounted = false;
    };
  }, []);

  // LEFT / CURRENT CONDITION STATS (Stagger: 0ms, 100ms, 200ms)
  const darjCrowd = useCountUp({
    target: metrics.darjCrowd,
    duration: 1600,
    delay: 0,
    decimals: 0,
    useGrouping: false,
    startTrigger: statsTriggered,
  });

  const darjTariff = useCountUp({
    target: metrics.darjTariff,
    duration: 1600,
    delay: 100,
    decimals: 0,
    useGrouping: true,
    startTrigger: statsTriggered,
  });

  const darjQueue = useCountUp({
    target: metrics.darjQueue,
    duration: 1600,
    delay: 200,
    decimals: 1,
    useGrouping: false,
    startTrigger: statsTriggered,
  });

  // RIGHT / ALTERNATIVE STATS (Stagger: 100ms, 200ms, 300ms)
  const kalCrowd = useCountUp({
    target: metrics.kalCrowd,
    duration: 1600,
    delay: 100,
    decimals: 0,
    useGrouping: false,
    startTrigger: statsTriggered,
  });

  const kalTariff = useCountUp({
    target: metrics.kalTariff,
    duration: 1600,
    delay: 200,
    decimals: 0,
    useGrouping: true,
    startTrigger: statsTriggered,
  });

  const kalWait = useCountUp({
    target: metrics.kalWait,
    duration: 1600,
    delay: 300,
    decimals: 0,
    useGrouping: false,
    startTrigger: statsTriggered,
  });

  return (
    <section
      ref={sectionRef}
      className="relative w-full z-10 overflow-hidden"
    >
      {/* ───────── Full-bleed cinematic background ───────── */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=2000&q=80"
          alt=""
          className="w-full h-full object-cover object-center filter brightness-[0.75] contrast-[1.08] saturate-[1.1]"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-stone-950/85 via-stone-950/70 to-stone-950/90" />
        <div className="absolute inset-0 bg-gradient-to-r from-stone-950/75 via-transparent to-stone-950/70" />
        {/* Subtle warm amber ambient glow to eliminate cold dark void */}
        <div className="absolute top-1/4 right-10 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        {/* Subtle grain texture */}
        <div className="absolute inset-0 opacity-[0.04] mix-blend-overlay" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noise\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noise)\'/%3E%3C/svg%3E")' }} />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-2 sm:pt-4 pb-20 sm:pb-28 space-y-12">

        {/* ═══════════════════════════════════════════════════════════════════════ */}
        {/* SECTION HEADER                                                        */}
        {/* ═══════════════════════════════════════════════════════════════════════ */}
        <div className={cn(
          'max-w-4xl space-y-5 transition-all duration-1000',
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        )}>
          {/* Pill badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.07] backdrop-blur-md border border-white/[0.12] text-amber-300 font-mono text-[11px] font-bold uppercase tracking-[0.2em]">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span>LIVE DECONGESTION IN ACTION</span>
          </div>

          <h2 className="text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold tracking-tight text-white leading-[1.08]">
            Don&apos;t just book.{' '}
            <span className="block mt-1 bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-200 bg-clip-text text-transparent">
              Redistribute the journey.
            </span>
          </h2>

          <p className="text-base sm:text-lg text-stone-300/90 font-light leading-relaxed max-w-2xl">
            Yatri Setu identifies destination pressure and guides travellers toward suitable
            alternatives — helping distribute tourism beyond overcrowded routes.
          </p>
        </div>

        {/* ═══════════════════════════════════════════════════════════════════════ */}
        {/* FLOW RIBBON: DARJEELING  ──▸  ALTERNATIVE FOUND  ──▸  KALIMPONG       */}
        {/* ═══════════════════════════════════════════════════════════════════════ */}
        <div className={cn(
          'flex flex-col md:flex-row items-center justify-between gap-4 p-5 rounded-2xl bg-white/[0.04] backdrop-blur-xl border border-white/[0.08] transition-all duration-1000 delay-200',
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
        )}>
          {/* From */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center">
              <MapPin className="w-4.5 h-4.5 text-rose-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-white">Darjeeling</span>
                <span className="px-2 py-0.5 rounded-md bg-rose-500/25 text-rose-300 font-mono text-[10px] font-bold border border-rose-500/20">
                  88 / 100
                </span>
              </div>
              <span className="text-[11px] font-mono text-rose-400/80 uppercase font-semibold tracking-wide">
                HIGH PRESSURE
              </span>
            </div>
          </div>

          {/* Connector */}
          <div className="flex items-center gap-3">
            <div className="hidden md:block w-12 h-px bg-gradient-to-r from-rose-500/40 to-amber-500/40" />
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-400/10 border border-amber-400/20 text-amber-300 font-mono text-[11px] font-bold tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
              <span>ALTERNATIVE FOUND</span>
            </div>
            <div className="hidden md:block w-12 h-px bg-gradient-to-r from-amber-500/40 to-emerald-500/40" />
          </div>

          {/* To */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
              <MapPin className="w-4.5 h-4.5 text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-white">Kalimpong</span>
                <span className="px-2 py-0.5 rounded-md bg-emerald-500/25 text-emerald-300 font-mono text-[10px] font-bold border border-emerald-500/20">
                  42 / 100
                </span>
              </div>
              <span className="text-[11px] font-mono text-emerald-400/80 uppercase font-semibold tracking-wide">
                BALANCED FLOW
              </span>
            </div>
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════════════ */}
        {/* SIDE-BY-SIDE COMPARISON: PREMIUM GLASSMORPHIC CARDS                   */}
        {/* ═══════════════════════════════════════════════════════════════════════ */}
        <div ref={statsRef} className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">

          {/* ─── CARD 1: DARJEELING (HOTSPOT) ─── */}
          <div className={cn(
            'group relative rounded-[1.75rem] overflow-hidden transition-all duration-1000 delay-300',
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          )}>
            {/* Card inner glow border */}
            <div className="absolute inset-0 rounded-[1.75rem] bg-gradient-to-b from-rose-500/20 via-rose-500/5 to-transparent p-[1px]">
              <div className="w-full h-full rounded-[1.75rem] bg-stone-950/80 backdrop-blur-2xl" />
            </div>

            <div className="relative z-10 p-7 sm:p-9 flex flex-col justify-between h-full space-y-7">
              {/* Header row */}
              <div className="flex items-center justify-between">
                <span className="px-3.5 py-1 rounded-full bg-rose-500/15 border border-rose-500/25 text-rose-300 font-mono text-[10px] font-extrabold uppercase tracking-[0.15em]">
                  TRADITIONAL CHOKED HOTSPOT
                </span>
                <div className="flex items-center gap-1.5 text-rose-400 font-mono text-[11px] font-bold">
                  <AlertTriangle className="w-3.5 h-3.5 animate-pulse" />
                  <span>Critical Density</span>
                </div>
              </div>

              {/* Title */}
              <div className="space-y-1.5">
                <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
                  Darjeeling Hill Station
                </h3>
                <p className="text-sm text-stone-400 font-light leading-relaxed">
                  Facing severe gridlock along Ghoom–Tiger Hill and water scarcity.
                </p>
              </div>

              {/* ── 3 METRIC TILES ── */}
              <div className="grid grid-cols-3 gap-3">
                {/* Crowd Score */}
                <div className="relative p-4 rounded-2xl bg-white/[0.04] border border-white/[0.06] text-center overflow-hidden group/tile">
                  <div className="absolute inset-0 bg-gradient-to-t from-rose-500/5 to-transparent opacity-0 group-hover/tile:opacity-100 transition-opacity" />
                  <div className="relative">
                    <div className="text-3xl sm:text-4xl font-black font-mono text-rose-400 tabular-nums">
                      {darjCrowd}<span className="text-lg text-rose-400/60">/100</span>
                    </div>
                    <div className="text-[9px] font-mono uppercase tracking-[0.15em] text-stone-500 font-semibold mt-1.5">
                      CROWD PRESSURE
                    </div>
                  </div>
                </div>

                {/* Avg Tariff */}
                <div className="relative p-4 rounded-2xl bg-white/[0.04] border border-white/[0.06] text-center overflow-hidden group/tile">
                  <div className="absolute inset-0 bg-gradient-to-t from-white/[0.02] to-transparent opacity-0 group-hover/tile:opacity-100 transition-opacity" />
                  <div className="relative">
                    <div className="text-3xl sm:text-4xl font-black font-mono text-white tabular-nums">
                      ₹{darjTariff}
                    </div>
                    <div className="text-[9px] font-mono uppercase tracking-[0.15em] text-stone-500 font-semibold mt-1.5">
                      AVG TARIFF / DAY
                    </div>
                  </div>
                </div>

                {/* Mall Rd Queue */}
                <div className="relative p-4 rounded-2xl bg-white/[0.04] border border-white/[0.06] text-center overflow-hidden group/tile">
                  <div className="absolute inset-0 bg-gradient-to-t from-rose-500/5 to-transparent opacity-0 group-hover/tile:opacity-100 transition-opacity" />
                  <div className="relative">
                    <div className="text-3xl sm:text-4xl font-black font-mono text-rose-400 tabular-nums">
                      {darjQueue}<span className="text-lg text-rose-400/60 ml-0.5">hrs</span>
                    </div>
                    <div className="text-[9px] font-mono uppercase tracking-[0.15em] text-stone-500 font-semibold mt-1.5">
                      MALL RD QUEUE
                    </div>
                  </div>
                </div>
              </div>

              {/* ── CONS (Red ✕ bullets) ── */}
              <div className="space-y-3 text-[13px] text-stone-300/90">
                <div className="flex items-start gap-3 p-3 rounded-xl bg-rose-500/[0.06] border border-rose-500/10">
                  <X className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" strokeWidth={2.5} />
                  <span>Overpriced surge tariffs during peak sunrise hours</span>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-rose-500/[0.06] border border-rose-500/10">
                  <X className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" strokeWidth={2.5} />
                  <span>Vehicle congestion causing severe carbon emission peaks</span>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-rose-500/[0.06] border border-rose-500/10">
                  <X className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" strokeWidth={2.5} />
                  <span>Less than 25% tourist spend reaches local indigenous communities</span>
                </div>
              </div>

              {/* ── ACTION BUTTON ── */}
              <Link
                href="/destinations/darjeeling/crowd"
                className="w-full h-13 rounded-2xl bg-white/[0.06] hover:bg-white/[0.10] border border-white/[0.10] hover:border-white/[0.18] text-white font-bold text-sm tracking-wide flex items-center justify-center gap-2.5 transition-all duration-300 backdrop-blur-md group/btn"
              >
                <Activity className="w-4 h-4 text-rose-400" />
                <span>Inspect Darjeeling Diagnostic Data</span>
                <ChevronRight className="w-4 h-4 text-stone-500 group-hover/btn:text-white group-hover/btn:translate-x-0.5 transition-all" />
              </Link>
            </div>
          </div>

          {/* ─── CARD 2: KALIMPONG (SANCTUARY MATCH) ─── */}
          <div className={cn(
            'group relative rounded-[1.75rem] overflow-hidden transition-all duration-1000 delay-500',
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          )}>
            {/* Card inner glow border */}
            <div className="absolute inset-0 rounded-[1.75rem] bg-gradient-to-b from-emerald-500/25 via-emerald-500/5 to-transparent p-[1px]">
              <div className="w-full h-full rounded-[1.75rem] bg-stone-950/80 backdrop-blur-2xl" />
            </div>

            <div className="relative z-10 p-7 sm:p-9 flex flex-col justify-between h-full space-y-7">
              {/* Header row */}
              <div className="flex items-center justify-between">
                <span className="px-3.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/25 text-emerald-300 font-mono text-[10px] font-extrabold uppercase tracking-[0.15em]">
                  RECOMMENDED SANCTUARY MATCH
                </span>
                <div className="flex items-center gap-1.5 text-emerald-400 font-mono text-[11px] font-bold">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>87% Similarity Match</span>
                </div>
              </div>

              {/* Title */}
              <div className="space-y-1.5">
                <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
                  Kalimpong Orchid Ridge
                </h3>
                <p className="text-sm text-stone-400 font-light leading-relaxed">
                  Same panoramic Kanchenjunga views, serene colonial cottages, and zero queue delays.
                </p>
              </div>

              {/* ── 3 METRIC TILES ── */}
              <div className="grid grid-cols-3 gap-3">
                {/* Crowd Score */}
                <div className="relative p-4 rounded-2xl bg-white/[0.04] border border-white/[0.06] text-center overflow-hidden group/tile">
                  <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/5 to-transparent opacity-0 group-hover/tile:opacity-100 transition-opacity" />
                  <div className="relative">
                    <div className="text-3xl sm:text-4xl font-black font-mono text-emerald-400 tabular-nums">
                      {kalCrowd}<span className="text-lg text-emerald-400/60">/100</span>
                    </div>
                    <div className="text-[9px] font-mono uppercase tracking-[0.15em] text-stone-500 font-semibold mt-1.5">
                      CROWD PRESSURE
                    </div>
                  </div>
                </div>

                {/* Avg Tariff */}
                <div className="relative p-4 rounded-2xl bg-white/[0.04] border border-white/[0.06] text-center overflow-hidden group/tile">
                  <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/5 to-transparent opacity-0 group-hover/tile:opacity-100 transition-opacity" />
                  <div className="relative">
                    <div className="text-3xl sm:text-4xl font-black font-mono text-emerald-300 tabular-nums">
                      ₹{kalTariff}
                    </div>
                    <div className="text-[9px] font-mono uppercase tracking-[0.15em] text-emerald-500 font-bold mt-1.5">
                      42% SAVINGS
                    </div>
                  </div>
                </div>

                {/* Entry Wait */}
                <div className="relative p-4 rounded-2xl bg-white/[0.04] border border-white/[0.06] text-center overflow-hidden group/tile">
                  <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/5 to-transparent opacity-0 group-hover/tile:opacity-100 transition-opacity" />
                  <div className="relative">
                    <div className="text-3xl sm:text-4xl font-black font-mono text-emerald-400 tabular-nums">
                      {kalWait}<span className="text-lg text-emerald-400/60 ml-1">mins</span>
                    </div>
                    <div className="text-[9px] font-mono uppercase tracking-[0.15em] text-stone-500 font-semibold mt-1.5">
                      ENTRY WAIT
                    </div>
                  </div>
                </div>
              </div>

              {/* ── PROS (Green ✓ bullets) ── */}
              <div className="space-y-3 text-[13px] text-stone-300/90">
                <div className="flex items-start gap-3 p-3 rounded-xl bg-emerald-500/[0.06] border border-emerald-500/10">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" strokeWidth={2.5} />
                  <span>Direct 90% homestay host revenue distribution via Panchayat</span>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-emerald-500/[0.06] border border-emerald-500/10">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" strokeWidth={2.5} />
                  <span>Quiet mountain trails and undisturbed pine canopy trails</span>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-emerald-500/[0.06] border border-emerald-500/10">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" strokeWidth={2.5} />
                  <span>Earn +30 Green Credits™ toward next Himalayan trip</span>
                </div>
              </div>

              {/* ── ACTION BUTTON ── */}
              <Link
                href="/destinations/darjeeling/alternatives"
                className="w-full h-13 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-sm tracking-wide shadow-lg shadow-emerald-900/40 flex items-center justify-center gap-2.5 transition-all duration-300 group/btn"
              >
                <span>Select Kalimpong Alternative</span>
                <ArrowRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>

        </div>



      </div>
    </section>
  );
}
