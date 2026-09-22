'use client';

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  ArrowUpRight,
  Compass,
  Flame,
  Activity,
  Sparkles,
  Layers,
  ChevronRight,
  TrendingDown,
  Info
} from 'lucide-react';
import { motion, AnimatePresence, useInView } from 'motion/react';
import { cn, formatINR } from '@/lib/utils';
import { fetchDestinations } from '@/lib/api';

export interface IntelligenceDestination {
  id: string;
  num: string;
  name: string;
  region: string;
  state: string;
  tagline: string;
  crowd_score: number | null;
  crowd_level: 'VERY HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' | null;
  avg_cost_per_day_inr: number | null;
  status_label: string;
  image: string;
  character_tags: string[];
  nearby_ids: string[];
  has_numerical_intelligence: boolean;
}

const DESTINATIONS_DATA: IntelligenceDestination[] = [
  {
    id: 'darjeeling',
    num: '01',
    name: 'Darjeeling',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    tagline: 'Colonial tea heritage and Himalayan railway landscapes facing heavy holiday congestion.',
    crowd_score: 88,
    crowd_level: 'VERY HIGH',
    avg_cost_per_day_inr: 4800,
    status_label: 'HIGH CONGESTION',
    image: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1600&q=85',
    character_tags: ['Heritage Rail', 'Tiger Hill', 'High Congestion'],
    nearby_ids: ['kalimpong', 'rishop', 'lava'],
    has_numerical_intelligence: true
  },
  {
    id: 'kalimpong',
    num: '02',
    name: 'Kalimpong',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    tagline: 'Tranquil orchid ridge, vibrant monasteries & balanced Himalayan flow.',
    crowd_score: 42,
    crowd_level: 'MEDIUM',
    avg_cost_per_day_inr: 2800,
    status_label: 'BALANCED FLOW',
    image: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1600&q=85',
    character_tags: ['Orchids', 'Serene Ridge', 'Monasteries'],
    nearby_ids: ['darjeeling', 'lava', 'rishop'],
    has_numerical_intelligence: true
  },
  {
    id: 'rishop',
    num: '03',
    name: 'Rishop',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    tagline: '360° panoramic Kanchenjunga sunrise haven without Tiger Hill queues.',
    crowd_score: 15,
    crowd_level: 'LOW',
    avg_cost_per_day_inr: 2200,
    status_label: 'SERENE REFUGE',
    image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=85',
    character_tags: ['Sunrise Ridge', 'Dark Sky', 'Zero Traffic'],
    nearby_ids: ['lava', 'kalimpong'],
    has_numerical_intelligence: true
  },
  {
    id: 'lava',
    num: '04',
    name: 'Lava',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    tagline: 'Misty pine woodlands & pristine gateway to Neora Valley National Park.',
    crowd_score: 24,
    crowd_level: 'LOW',
    avg_cost_per_day_inr: 2100,
    status_label: 'OPEN TRAILS',
    image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1600&q=85',
    character_tags: ['Pine Forest', 'Birding', 'Misty Trails'],
    nearby_ids: ['rishop', 'kalimpong'],
    has_numerical_intelligence: true
  },
  {
    id: 'sillery-gaon',
    num: '05',
    name: 'Sillery Gaon',
    region: 'Eastern Himalayas',
    state: 'Kalimpong District',
    tagline: 'Secluded Lepcha mountain hamlet known as New Darjeeling, untouched by mass transit.',
    crowd_score: null,
    crowd_level: null,
    avg_cost_per_day_inr: null,
    status_label: 'DISCOVERY EN ROUTE',
    image: 'https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=1600&q=85',
    character_tags: ['Silent Hamlet', 'Canopy Views', 'Homesteads'],
    nearby_ids: ['lava', 'rishop'],
    has_numerical_intelligence: false
  },
  {
    id: 'sandakphu',
    num: '06',
    name: 'Sandakphu',
    region: 'Singalila Ridge',
    state: 'Indo-Nepal Border',
    tagline: 'Highest peak in West Bengal offering the legendary Sleeping Buddha panoramic vista.',
    crowd_score: null,
    crowd_level: null,
    avg_cost_per_day_inr: null,
    status_label: 'EXPEDITION TRAIL',
    image: 'https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=1600&q=85',
    character_tags: ['Singalila Ridge', 'Sleeping Buddha', 'High Altitude'],
    nearby_ids: ['darjeeling'],
    has_numerical_intelligence: false
  }
];

// Smooth numerical counter interpolation hook (500-700ms)
function useAnimatedCounter(target: number | null, duration = 600) {
  const [displayValue, setDisplayValue] = useState<number | null>(target);
  const prevValueRef = useRef<number | null>(target);

  useEffect(() => {
    if (target === null) {
      setDisplayValue(null);
      prevValueRef.current = null;
      return;
    }

    const start = prevValueRef.current ?? target;
    const diff = target - start;
    if (diff === 0) {
      setDisplayValue(target);
      return;
    }

    const startTime = performance.now();
    let animId: number;

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duration);
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + diff * ease);
      setDisplayValue(current);

      if (progress < 1) {
        animId = requestAnimationFrame(tick);
      } else {
        prevValueRef.current = target;
      }
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [target, duration]);

  return displayValue;
}

export function DestinationIntelligence() {
  const [destinations, setDestinations] = useState<IntelligenceDestination[]>(DESTINATIONS_DATA);
  const [activeId, setActiveId] = useState<string>('darjeeling');
  const [hoveredSecondaryId, setHoveredSecondaryId] = useState<string | null>(null);
  const [mouseOffset, setMouseOffset] = useState({ x: 0, y: 0 });
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  const sectionRef = useRef<HTMLElement>(null);
  const mainCardRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, amount: 0.25 });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const media = window.matchMedia('(prefers-reduced-motion: reduce)');
      setIsReducedMotion(media.matches);
      const listener = (e: MediaQueryListEvent) => setIsReducedMotion(e.matches);
      media.addEventListener('change', listener);
      return () => media.removeEventListener('change', listener);
    }
  }, []);

  // Fetch real telemetry data on mount to supersede mock fallbacks
  useEffect(() => {
    let isMounted = true;
    async function loadLiveData() {
      try {
        const liveList = await fetchDestinations();
        if (!isMounted || !liveList || liveList.length === 0) return;

        setDestinations((prev) =>
          prev.map((dest) => {
            const match = liveList.find((d) => d.id.toLowerCase() === dest.id.toLowerCase());
            if (!match) return dest;

            let status_label = dest.status_label;
            if (match.crowd_level === 'VERY HIGH' || match.crowd_level === 'HIGH') {
              status_label = 'HIGH CONGESTION';
            } else if (match.crowd_level === 'MEDIUM') {
              status_label = 'BALANCED FLOW';
            } else if (match.crowd_level === 'LOW') {
              status_label = match.crowd_score <= 18 ? 'SERENE REFUGE' : 'OPEN TRAILS';
            }

            return {
              ...dest,
              crowd_score: match.crowd_score,
              crowd_level: match.crowd_level as any,
              avg_cost_per_day_inr: match.avg_cost_per_day_inr || dest.avg_cost_per_day_inr,
              status_label,
              has_numerical_intelligence: true
            };
          })
        );
      } catch (err) {
        console.warn('DestinationIntelligence live fetch fallback active:', err);
      }
    }
    loadLiveData();
    return () => {
      isMounted = false;
    };
  }, []);

  // Active destination
  const activeDest = useMemo(() => {
    return destinations.find((d) => d.id === activeId) || destinations[0];
  }, [destinations, activeId]);

  // Secondary destinations (all other destinations)
  const secondaryDestinations = useMemo(() => {
    return destinations.filter((d) => d.id !== activeId);
  }, [destinations, activeId]);

  // Primary 3 secondary cards for desktop asymmetric grid
  const primarySecondaryCards = secondaryDestinations.slice(0, 3);
  // Remaining secondary cards accessible via compact control
  const extendedSecondaryCards = secondaryDestinations.slice(3);

  // Interpolated numerical scores
  const animatedCrowdScore = useAnimatedCounter(activeDest.crowd_score, 600);
  const animatedCost = useAnimatedCounter(activeDest.avg_cost_per_day_inr, 600);

  // Mouse follow on main image only (shifts 6-10px) - disabled on touch devices
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!mainCardRef.current || isReducedMotion) return;
    if (typeof window !== 'undefined' && window.matchMedia && !window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      return;
    }
    const rect = mainCardRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 16; // -8px to +8px
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 16; // -8px to +8px
    setMouseOffset({ x, y });
  }, [isReducedMotion]);

  const handleMouseLeave = useCallback(() => {
    setMouseOffset({ x: 0, y: 0 });
  }, []);

  // Handler for selecting/promoting a destination
  const handleSelectDestination = (id: string) => {
    if (id === activeId) return;
    setActiveId(id);
  };

  // Vertical pressure calculation:
  // Diagram:
  // LOW
  //  │
  //  ●
  // HIGH
  // If score is 88 (Darjeeling): near HIGH (near bottom = ~88%)
  // If score is 42 (Kalimpong): middle (~42%)
  // If score is 15 or 24 (Rishop/Lava): near LOW (~15% - 24%)
  const verticalPressurePercent = activeDest.crowd_score !== null
    ? Math.min(88, Math.max(12, activeDest.crowd_score))
    : 50;

  // Hovered target info for main card visual response
  const hoveredDest = hoveredSecondaryId
    ? destinations.find((d) => d.id === hoveredSecondaryId)
    : null;

  return (
    <section
      ref={sectionRef}
      className="relative w-full py-20 lg:py-24 z-10 border-t border-stone-200/70 dark:border-stone-800/70"
      aria-label="Destination Intelligence Engine"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* ================================================== */}
        {/* SECTION HEADER                                     */}
        {/* ================================================== */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-12 lg:mb-14 pb-6 border-b border-stone-200/80 dark:border-stone-800">
          <div className="max-w-2xl">
            {/* Eyebrow */}
            <motion.div
              initial={isReducedMotion ? {} : { opacity: 0, y: 12 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="flex items-center gap-2 mb-3"
            >
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              <span className="text-xs font-mono font-bold uppercase tracking-widest text-amber-700 dark:text-amber-400">
                DESTINATION INTELLIGENCE
              </span>
            </motion.div>

            {/* Title */}
            <motion.h2
              initial={isReducedMotion ? {} : { opacity: 0, y: 18 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-stone-950 dark:text-white tracking-tight leading-[1.08]"
            >
              ESCAPE THE PRESSURE.
              <br />
              <span className="font-serif italic font-normal text-stone-800 dark:text-stone-300">
                FIND YOUR PLACE.
              </span>
            </motion.h2>

            {/* Supporting Text */}
            <motion.p
              initial={isReducedMotion ? {} : { opacity: 0, y: 14 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="text-sm sm:text-base text-stone-600 dark:text-stone-400 mt-3 font-normal leading-relaxed"
            >
              Compare crowd pressure, daily cost and destination character before you choose your Himalayan escape.
            </motion.p>
          </div>

          {/* Small Elegant CTA on the Right */}
          <motion.div
            initial={isReducedMotion ? {} : { opacity: 0, x: 16 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center"
          >
            <Link
              href="/destinations"
              className="group inline-flex items-center gap-2 text-xs font-bold tracking-wider uppercase text-stone-900 dark:text-stone-100 hover:text-amber-600 dark:hover:text-amber-400 transition-colors py-2 px-3.5 rounded-lg border border-stone-300/80 dark:border-stone-700 hover:border-amber-500/60 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm"
            >
              <span>VIEW ALL SANCTUARIES</span>
              <ArrowRight className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-1 text-amber-600 dark:text-amber-400" />
            </Link>
          </motion.div>
        </div>

        {/* ================================================== */}
        {/* MAIN EDITORIAL LAYOUT (CSS GRID)                   */}
        {/* ================================================== */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          
          {/* -------------------------------------------------- */}
          {/* MAIN DESTINATION CARD (~58% visual area on desktop)*/}
          {/* -------------------------------------------------- */}
          <div className="lg:col-span-7 flex flex-col">
            <div
              ref={mainCardRef}
              onMouseMove={handleMouseMove}
              onMouseLeave={handleMouseLeave}
              className={cn(
                'relative w-full min-h-[580px] lg:min-h-[640px] rounded-3xl overflow-hidden shadow-2xl border transition-all duration-500 flex flex-col justify-between p-6 sm:p-8 lg:p-10 select-none bg-stone-950 text-white',
                hoveredSecondaryId
                  ? 'border-amber-500/60 ring-2 ring-amber-500/20'
                  : 'border-stone-800/90'
              )}
            >
              {/* Full-bleed Image with Editorial Clip-Path Reveal */}
              <motion.div
                initial={isReducedMotion ? {} : { clipPath: 'inset(0 100% 0 0)' }}
                animate={isInView ? { clipPath: 'inset(0 0% 0 0)' } : {}}
                transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                className="absolute inset-0 overflow-hidden"
              >
                <AnimatePresence mode="wait">
                  <motion.img
                    key={activeDest.id}
                    src={activeDest.image}
                    alt={activeDest.name}
                    initial={{ opacity: 0, scale: 1.08 }}
                    animate={{ opacity: 1, scale: 1.04 }}
                    exit={{ opacity: 0, scale: 1.0 }}
                    transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                    style={{
                      transform: isReducedMotion
                        ? 'scale(1.04)'
                        : `translate3d(${mouseOffset.x}px, ${mouseOffset.y}px, 0) scale(1.04)`,
                      transition: 'transform 0.18s ease-out'
                    }}
                    className="w-full h-full object-cover filter brightness-[0.92]"
                    loading="eager"
                  />
                </AnimatePresence>

                {/* Subtle dark gradient from bottom upward */}
                <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/50 to-stone-950/20 pointer-events-none" />
                {/* Subtle film grain texture */}
                <div className="absolute inset-0 bg-[radial-gradient(#ffffff_0.5px,transparent_0.5px)] opacity-[0.03] pointer-events-none" />
              </motion.div>

              {/* ================= TOP ROW ================= */}
              <div className="relative z-10 flex items-start justify-between gap-4">
                {/* Top-Left: DESTINATION 01 */}
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/45 backdrop-blur-md border border-white/10 text-[11px] font-mono tracking-widest uppercase text-stone-200">
                  <span className="text-amber-400 font-bold">●</span>
                  <span>DESTINATION {activeDest.num}</span>
                </div>

                {/* Top-Right: Crowd Level + Score with Subtle Pressure Pulse */}
                <div className="flex flex-col items-end">
                  <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/55 backdrop-blur-md border border-white/15 text-xs font-mono font-bold tracking-wider text-white">
                    {/* Pressure Pulse Dot */}
                    <span className="relative flex h-2 w-2">
                      {activeDest.crowd_level === 'VERY HIGH' && (
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-60" />
                      )}
                      {activeDest.crowd_level === 'MEDIUM' && (
                        <span className="animate-pulse absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-40" />
                      )}
                      <span
                        className={cn(
                          'relative inline-flex rounded-full h-2 w-2',
                          activeDest.crowd_level === 'VERY HIGH' && 'bg-rose-500',
                          activeDest.crowd_level === 'MEDIUM' && 'bg-amber-400',
                          activeDest.crowd_level === 'LOW' && 'bg-emerald-400',
                          !activeDest.crowd_level && 'bg-stone-400'
                        )}
                      />
                    </span>

                    {/* Numeric Score */}
                    <span>
                      {activeDest.has_numerical_intelligence && animatedCrowdScore !== null
                        ? `${animatedCrowdScore} / 100`
                        : 'TELEMETRY PENDING'}
                    </span>
                  </div>

                  {/* Status Level Badge */}
                  <span
                    className={cn(
                      'text-[10px] font-mono tracking-widest uppercase mt-1 px-1 font-semibold',
                      activeDest.crowd_level === 'VERY HIGH' && 'text-rose-400',
                      activeDest.crowd_level === 'MEDIUM' && 'text-amber-300',
                      activeDest.crowd_level === 'LOW' && 'text-emerald-400',
                      !activeDest.crowd_level && 'text-stone-400'
                    )}
                  >
                    {activeDest.crowd_level ? activeDest.crowd_level : 'UNMONITORED'}
                  </span>
                </div>
              </div>

              {/* Hover response pill if a secondary destination is active */}
              {hoveredDest && (
                <div className="relative z-10 self-start mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 backdrop-blur-md border border-amber-400/40 text-[10px] font-mono text-amber-200 animate-fadeIn">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                  <span>COMPARING WITH {hoveredDest.name.toUpperCase()} (CLICK CARD TO SWAP)</span>
                </div>
              )}

              {/* ================= BOTTOM CONTENT ================= */}
              <div className="relative z-10 flex flex-col gap-6 mt-auto pt-10">
                {/* Title and Tagline Crossfade */}
                <div className="overflow-hidden">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeDest.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    >
                      <h3 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white uppercase font-sans">
                        {activeDest.name}
                      </h3>

                      <p className="text-xs sm:text-sm font-mono tracking-wider uppercase text-amber-300/90 mt-1 font-semibold">
                        {activeDest.region} · {activeDest.state}
                      </p>

                      <p className="text-sm sm:text-base text-stone-200 mt-2.5 max-w-xl font-normal leading-relaxed text-balance">
                        {activeDest.tagline}
                      </p>
                    </motion.div>
                  </AnimatePresence>
                </div>

                {/* Intelligence Metrics Row + Vertical Pressure Indicator */}
                <div className="p-4 sm:p-5 rounded-2xl bg-black/45 backdrop-blur-md border border-white/10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-5">
                  
                  {/* Metric Columns */}
                  <div className="grid grid-cols-3 gap-3 sm:gap-4 flex-1">
                    {/* Metric 1: Crowd Pressure */}
                    <div className="border-r border-white/10 pr-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-stone-400 block font-semibold">
                        CROWD PRESSURE
                      </span>
                      <span className="text-lg sm:text-xl font-mono font-extrabold text-white mt-0.5 block">
                        {activeDest.has_numerical_intelligence && animatedCrowdScore !== null
                          ? `${animatedCrowdScore} / 100`
                          : '—'}
                      </span>
                      <span className="text-[10px] text-stone-400 font-mono">
                        {activeDest.crowd_level || 'Pending'}
                      </span>
                    </div>

                    {/* Metric 2: Avg Daily */}
                    <div className="border-r border-white/10 pr-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-stone-400 block font-semibold">
                        AVG DAILY
                      </span>
                      <span className="text-lg sm:text-xl font-mono font-extrabold text-white mt-0.5 block">
                        {activeDest.has_numerical_intelligence && animatedCost !== null
                          ? formatINR(animatedCost)
                          : '—'}
                      </span>
                      <span className="text-[10px] text-stone-400 font-mono">
                        {activeDest.has_numerical_intelligence ? 'Per traveler' : 'Field Survey'}
                      </span>
                    </div>

                    {/* Metric 3: Status */}
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-stone-400 block font-semibold">
                        STATUS
                      </span>
                      <span className="text-xs font-mono font-extrabold text-amber-400 mt-1 block uppercase tracking-tight leading-tight">
                        {activeDest.status_label}
                      </span>
                      <span className="text-[10px] text-stone-400 font-mono">
                        Flow telemetry
                      </span>
                    </div>
                  </div>

                  {/* Vertical Crowd Pressure Indicator */}
                  <div className="sm:border-l sm:border-white/10 sm:pl-5 flex items-center justify-between sm:justify-start gap-4">
                    <div className="flex flex-col items-center">
                      <span className="text-[8px] font-mono uppercase tracking-wider text-stone-400 font-semibold mb-0.5">
                        PRESSURE
                      </span>
                      <span className="text-[9px] font-mono text-stone-400 tracking-wider">LOW</span>
                      
                      {/* Vertical Gauge Track */}
                      <div className="w-[2px] h-16 bg-stone-700/80 my-1 relative rounded-full">
                        {/* Gradation marks */}
                        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-1.5 h-[1px] bg-stone-600" />
                        <div className="absolute top-2/4 left-1/2 -translate-x-1/2 w-2 h-[1px] bg-stone-500" />
                        <div className="absolute top-3/4 left-1/2 -translate-x-1/2 w-1.5 h-[1px] bg-stone-600" />

                        {/* Smoothly moving marker */}
                        <div
                          style={{
                            top: `${verticalPressurePercent}%`,
                            transform: 'translate(-50%, -50%)',
                            transition: 'top 600ms cubic-bezier(0.16, 1, 0.3, 1)'
                          }}
                          className="absolute left-1/2"
                        >
                          <div className="relative flex items-center justify-center">
                            {/* Pressure pulse micro-interaction */}
                            {activeDest.crowd_level === 'VERY HIGH' && (
                              <span className="absolute -inset-1 rounded-full border border-rose-400 animate-ping opacity-60" />
                            )}
                            {activeDest.crowd_level === 'MEDIUM' && (
                              <span className="absolute -inset-0.5 rounded-full border border-amber-400 animate-pulse opacity-40" />
                            )}
                            <div
                              className={cn(
                                'w-3 h-3 rounded-full shadow-md border border-black/40',
                                activeDest.crowd_level === 'VERY HIGH' && 'bg-rose-500',
                                activeDest.crowd_level === 'MEDIUM' && 'bg-amber-400',
                                activeDest.crowd_level === 'LOW' && 'bg-emerald-400',
                                !activeDest.crowd_level && 'bg-stone-300'
                              )}
                            />
                          </div>
                        </div>
                      </div>
                      <span className="text-[9px] font-mono text-stone-400 tracking-wider">HIGH</span>
                    </div>

                    {/* Explore Link */}
                    <Link
                      href={`/destinations/${activeDest.id}`}
                      className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-stone-950 font-bold text-xs transition-colors shadow-sm"
                      title={`Explore ${activeDest.name}`}
                    >
                      <span>Explore</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>

                {/* ================================================== */}
                {/* UNIQUE INTERACTION: DESTINATION ORBIT              */}
                {/* ================================================== */}
                <div className="pt-2 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono uppercase tracking-widest text-stone-400 font-semibold flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                      EXPLORE NEARBY
                    </span>
                    <span className="text-[10px] text-stone-500 hidden sm:inline">|</span>
                  </div>

                  {/* Connected Orbit Chips */}
                  <div className="flex flex-wrap items-center gap-2">
                    {activeDest.nearby_ids.map((nid) => {
                      const targetDest = destinations.find((d) => d.id === nid);
                      if (!targetDest) return null;
                      const isHovered = hoveredSecondaryId === nid;

                      return (
                        <button
                          key={nid}
                          type="button"
                          onClick={() => handleSelectDestination(nid)}
                          onMouseEnter={() => setHoveredSecondaryId(nid)}
                          onMouseLeave={() => setHoveredSecondaryId(null)}
                          className={cn(
                            'group relative inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono tracking-wider uppercase transition-all duration-300 border cursor-pointer',
                            isHovered
                              ? 'bg-amber-500/25 text-amber-200 border-amber-400 shadow-sm'
                              : 'bg-black/40 hover:bg-black/60 text-stone-300 border-white/10 hover:border-white/30'
                          )}
                        >
                          {/* Connection line stroke that lights up on hover */}
                          <span
                            className={cn(
                              'w-2 h-[1px] transition-all duration-300',
                              isHovered ? 'w-3.5 bg-amber-400' : 'bg-stone-500/60'
                            )}
                          />
                          <span>{targetDest.name}</span>
                          <ArrowUpRight
                            className={cn(
                              'w-2.5 h-2.5 transition-transform duration-300',
                              isHovered ? 'translate-x-0.5 -translate-y-0.5 text-amber-300' : 'text-stone-400'
                            )}
                          />
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* -------------------------------------------------- */}
          {/* SECONDARY DESTINATION CARDS (Asymmetric Deck)      */}
          {/* -------------------------------------------------- */}
          <div className="lg:col-span-5 flex flex-col justify-between gap-4">
            
            {/* Editorial Comparison Header */}
            <div className="flex items-center justify-between pb-2 border-b border-stone-200 dark:border-stone-800">
              <span className="text-xs font-mono font-bold uppercase tracking-widest text-stone-500 dark:text-stone-400">
                COMPARISON DECK ({secondaryDestinations.length} NODES)
              </span>
              <span className="text-[10px] font-mono text-stone-400">
                CLICK TO PROMOTE
              </span>
            </div>

            {/* Asymmetrical Secondary Cards Container */}
            {/* Desktop: vertical asymmetric flow. Mobile: 2-column compact grid */}
            <div className="grid grid-cols-2 lg:grid-cols-1 gap-3 sm:gap-4 flex-1">
              {primarySecondaryCards.map((dest, idx) => {
                const isHovered = hoveredSecondaryId === dest.id;

                return (
                  <motion.div
                    key={dest.id}
                    initial={isReducedMotion ? {} : { opacity: 0, y: 20 + idx * 10 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{
                      duration: 0.6,
                      delay: 0.2 + idx * 0.1,
                      ease: [0.16, 1, 0.3, 1]
                    }}
                    onClick={() => handleSelectDestination(dest.id)}
                    onMouseEnter={() => setHoveredSecondaryId(dest.id)}
                    onMouseLeave={() => setHoveredSecondaryId(null)}
                    className={cn(
                      'group relative rounded-2xl overflow-hidden cursor-pointer border transition-all duration-500 ease-out flex flex-col justify-between min-h-[150px] sm:min-h-[170px] p-4 sm:p-5 select-none bg-stone-900',
                      isHovered
                        ? 'border-amber-500/80 shadow-xl -translate-y-2 ring-1 ring-amber-500/30'
                        : 'border-stone-200/80 dark:border-stone-800 hover:border-stone-400'
                    )}
                  >
                    {/* Photography with Grayscale Transition (55% -> 15% on hover, 0% active) */}
                    <div className="absolute inset-0 overflow-hidden">
                      <img
                        src={dest.image}
                        alt={dest.name}
                        className={cn(
                          'w-full h-full object-cover transition-all duration-700 ease-out',
                          isHovered
                            ? 'scale-106 filter grayscale-[15%] brightness-100'
                            : 'scale-100 filter grayscale-[55%] brightness-[0.85]'
                        )}
                        loading="lazy"
                      />
                      {/* Gradient overlay */}
                      <div className="absolute inset-0 bg-gradient-to-t from-stone-950/90 via-stone-950/40 to-stone-950/20" />
                    </div>

                    {/* Top Row: Index & Crowd Indicator */}
                    <div className="relative z-10 flex items-center justify-between gap-1.5">
                      <span className="text-[10px] sm:text-[11px] font-mono tracking-widest uppercase text-amber-300 font-bold bg-black/40 px-2 py-0.5 rounded-md backdrop-blur-sm border border-white/10">
                        {dest.num}
                      </span>

                      {/* Small crowd indicator */}
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-black/50 backdrop-blur-sm border border-white/10 text-[9px] sm:text-[10px] font-mono text-white">
                        {dest.has_numerical_intelligence ? (
                          <>
                            <span
                              className={cn(
                                'w-1.5 h-1.5 rounded-full',
                                dest.crowd_level === 'VERY HIGH' && 'bg-rose-500',
                                dest.crowd_level === 'MEDIUM' && 'bg-amber-400',
                                dest.crowd_level === 'LOW' && 'bg-emerald-400'
                              )}
                            />
                            <span>{dest.crowd_score} / 100</span>
                            <span className="text-stone-400 font-sans hidden sm:inline">·</span>
                            <span className="font-semibold text-stone-200 hidden sm:inline">{dest.crowd_level}</span>
                          </>
                        ) : (
                          <span className="text-stone-300 truncate max-w-[80px] sm:max-w-none">{dest.status_label}</span>
                        )}
                      </div>
                    </div>

                    {/* Bottom Row: Destination Name + Arrow on Hover */}
                    <div className="relative z-10 pt-4 flex items-end justify-between">
                      <div>
                        <h4
                          className={cn(
                            'text-lg sm:text-2xl font-bold uppercase tracking-tight text-white transition-transform duration-500',
                            isHovered && '-translate-y-1 text-amber-200'
                          )}
                        >
                          {dest.name}
                        </h4>
                        <p className="text-[10px] sm:text-[11px] font-mono text-stone-300 mt-0.5 truncate max-w-[140px] sm:max-w-none">
                          {dest.region}
                        </p>
                      </div>

                      {/* Small arrow appearing on hover */}
                      <div
                        className={cn(
                          'w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-amber-500 text-stone-950 flex items-center justify-center transition-all duration-300',
                          isHovered
                            ? 'opacity-100 translate-x-0 scale-100'
                            : 'opacity-0 translate-x-2 scale-75'
                        )}
                      >
                        <ArrowUpRight className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Compact "More Destinations" Control (05 SILLERY GAON · 06 SANDAKPHU) */}
            <div className="pt-2 border-t border-stone-200/80 dark:border-stone-800">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono uppercase tracking-wider text-stone-500 dark:text-stone-400 font-semibold">
                  ADDITIONAL CIRCUIT NODES
                </span>
                <span className="text-[10px] font-mono text-amber-600 dark:text-amber-400">
                  FRONTIER SANCTUARIES
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                {extendedSecondaryCards.map((dest) => {
                  const isHovered = hoveredSecondaryId === dest.id;

                  return (
                    <button
                      key={dest.id}
                      type="button"
                      onClick={() => handleSelectDestination(dest.id)}
                      onMouseEnter={() => setHoveredSecondaryId(dest.id)}
                      onMouseLeave={() => setHoveredSecondaryId(null)}
                      className={cn(
                        'relative rounded-xl overflow-hidden p-3 text-left border transition-all duration-300 flex items-center justify-between group cursor-pointer bg-stone-900',
                        isHovered
                          ? 'border-amber-500/80 -translate-y-1 shadow-md'
                          : 'border-stone-200/80 dark:border-stone-800'
                      )}
                    >
                      {/* Background image subtle preview */}
                      <div className="absolute inset-0 overflow-hidden">
                        <img
                          src={dest.image}
                          alt={dest.name}
                          className="w-full h-full object-cover filter grayscale-[65%] opacity-30 group-hover:opacity-45 group-hover:scale-105 transition-all duration-500"
                          loading="lazy"
                        />
                        <div className="absolute inset-0 bg-stone-950/80" />
                      </div>

                      <div className="relative z-10">
                        <span className="text-[9px] font-mono text-amber-400 block font-bold">
                          {dest.num}
                        </span>
                        <span className="text-xs font-bold text-white uppercase tracking-tight block">
                          {dest.name}
                        </span>
                        <span className="text-[9px] font-mono text-stone-400 truncate block max-w-[100px] sm:max-w-[120px]">
                          {dest.region}
                        </span>
                      </div>

                      <div className="relative z-10 w-6 h-6 rounded-full bg-white/10 group-hover:bg-amber-500 group-hover:text-stone-950 text-white flex items-center justify-center transition-colors">
                        <ArrowUpRight className="w-3 h-3" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

          </div>

        </div>

        {/* ================================================== */}
        {/* BOTTOM INFORMATION STRIP                           */}
        {/* ================================================== */}
        <motion.div
          initial={isReducedMotion ? {} : { opacity: 0, y: 12 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="mt-14 pt-6 border-t border-stone-200/80 dark:border-stone-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono tracking-widest uppercase text-stone-500 dark:text-stone-400"
        >
          <div className="flex items-center gap-2 font-bold text-stone-900 dark:text-stone-200">
            <span className="w-2 h-2 rounded-sm bg-amber-500" />
            <span>YATRI SETU INTELLIGENCE</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-x-4 sm:gap-x-6 gap-y-2 text-[10px] sm:text-[11px]">
            <span>CROWD PRESSURE</span>
            <span className="text-stone-300 dark:text-stone-700">·</span>
            <span>TRAVEL COST</span>
            <span className="text-stone-300 dark:text-stone-700">·</span>
            <span>DESTINATION CHARACTER</span>
            <span className="text-stone-300 dark:text-stone-700">·</span>
            <span>LOCAL EXPERIENCE</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
