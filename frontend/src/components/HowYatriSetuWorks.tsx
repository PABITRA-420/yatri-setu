'use client';

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  ArrowUpRight,
  Sparkles,
  Shield,
  Activity,
  Flame,
  RadioTower,
  MapPin,
  Clock,
  Home as HomeIcon,
  CheckCircle2,
  Compass,
  Layers,
  Leaf,
  Users,
  ChevronDown
} from 'lucide-react';
import { motion, AnimatePresence, useInView } from 'motion/react';
import { cn, formatINR } from '@/lib/utils';

// ============================================================================
// DATA & TYPES
// ============================================================================

export interface FeatureChapter {
  id: string;
  step: string;
  badge: string;
  navTitle: string;
  chapterTitle: string;
  storyHeading: string;
  storyLead: string;
  storyDetail: string;
  actionUrl: string;
  actionText: string;
  metricLabel?: string;
  metricValue?: number;
  metricSuffix?: string;
  metricSub?: string;
  technicalLabel: string;
}

const FEATURE_CHAPTERS: FeatureChapter[] = [
  {
    id: 'bottleneck-detection',
    step: '01',
    badge: 'Score: 88/100 Alert',
    navTitle: 'Real-Time Bottleneck Detection',
    chapterTitle: 'REAL-TIME BOTTLENECK DETECTION',
    storyHeading: 'Before committing to a ridge, see the invisible gridlock.',
    storyLead:
      'Tourist demand clusters predictably around iconic Himalayan landmarks. Before a traveler books or departs, Yatri Setu evaluates physical carrying capacities to expose impending holiday saturation.',
    storyDetail:
      'Simulated multi-factor telemetry evaluates vehicular congestion along Hill Cart Road, parking saturation near Tiger Hill, and municipal water stresses before visitors get stranded in hours-long traffic.',
    actionUrl: '/destinations/darjeeling/crowd',
    actionText: 'Inspect Darjeeling Diagnostics',
    metricLabel: 'CROWD PRESSURE SCORE',
    metricValue: 88,
    metricSuffix: ' / 100',
    metricSub: 'CRITICAL CONGESTION THRESHOLD',
    technicalLabel: '6-FACTOR DECONGESTION TELEMETRY'
  },
  {
    id: 'similarity-match',
    step: '02',
    badge: '87% Similarity',
    navTitle: 'AI Similarity & Capacity Match',
    chapterTitle: 'AI SIMILARITY & CAPACITY MATCH',
    storyHeading: 'When pressure rises, discover a tranquil sister sanctuary.',
    storyLead:
      'Rather than blocking travelers, Yatri Setu pairs crowded hotspots with ecologically matched sister hamlets that deliver the exact Himalayan character without the holiday stress.',
    storyDetail:
      'When Darjeeling exceeds optimal limits, our affinity model highlights Kalimpong and Rishop—offering 360° Kanchenjunga panoramas, tranquil orchid nurseries, and 42% lower daily travel tariffs with zero queues.',
    actionUrl: '/destinations/darjeeling/alternatives',
    actionText: 'View Alternative Advisor',
    metricLabel: 'EXPERIENTIAL AFFINITY',
    metricValue: 87,
    metricSuffix: '%',
    metricSub: 'MATCHED WITH KALIMPONG RIDGE',
    technicalLabel: 'CAPACITY-BALANCED REDIRECTION'
  },
  {
    id: 'crowd-smart-itinerary',
    step: '03',
    badge: 'Day-by-Day Flow',
    navTitle: 'Adaptive Crowd-Smart Itinerary',
    chapterTitle: 'ADAPTIVE CROWD-SMART ITINERARY',
    storyHeading: 'Pace your travel by the natural rhythm of the mountains.',
    storyLead:
      'Turn destination choices into an unhurried day-by-day expedition tailored around off-peak trail hours, local artisans, and secluded viewpoints.',
    storyDetail:
      'The flow generator staggers morning departures, directs lunch stops toward indigenous Lepcha cooperatives, and guides you to quiet sunset viewpoints while mass tour buses congest the main highways.',
    actionUrl: '/itinerary',
    actionText: 'Try Itinerary Planner',
    metricLabel: 'PEAK QUEUE REDUCTION',
    metricValue: 65,
    metricSuffix: '%',
    metricSub: 'OPTIMIZED TIME-BLOCKING',
    technicalLabel: 'TEMPORAL FLOW OPTIMIZATION'
  },
  {
    id: 'panchayat-booking',
    step: '04',
    badge: '90% Direct Host Share',
    navTitle: 'Direct Panchayat Host Booking',
    chapterTitle: 'DIRECT PANCHAYAT HOST BOOKING',
    storyHeading: 'Keep your journey in the hands of the mountain community.',
    storyLead:
      'Direct community reservations bypass exploitative intermediaries, ensuring rural families receive the lion’s share of tourism expenditure.',
    storyDetail:
      'Stay in verified village wooden cottages endorsed by local Panchayats. Your bookings fund trail maintenance, sustainable waste processing, and local youth mountain guides while earning you Green Credit incentives.',
    actionUrl: '/homestays',
    actionText: 'Browse Panchayat Stays',
    metricLabel: 'DIRECT HOST REVENUE SHARE',
    metricValue: 90,
    metricSuffix: '%',
    metricSub: 'VERIFIED PANCHAYAT LEDGER',
    technicalLabel: 'COMMUNITY LEDGER SETTLEMENT'
  },
  {
    id: 'emergency-net',
    step: '05',
    badge: 'National 112 & GPS',
    navTitle: 'Yatri Mitra Emergency Net (SOS)',
    chapterTitle: 'YATRI MITRA EMERGENCY NET (SOS)',
    storyHeading: 'Peace of mind in every valley, with location-aware safety.',
    storyLead:
      'High-altitude Himalayan adventures demand calm, dependable safety infrastructure integrated seamlessly into your journey.',
    storyDetail:
      'One-tap Yatri Mitra assistance shares exact offline coordinates with local volunteer wardens, homestay associations, and the national 112 emergency network to ensure rapid assistance across remote trails.',
    actionUrl: '/safety/sos',
    actionText: 'Launch Safety SOS Terminal',
    metricLabel: 'DISPATCH INTEGRATION',
    metricValue: 112,
    metricSuffix: ' READY',
    metricSub: 'GPS + VILLAGE MESH BACKBONE',
    technicalLabel: 'CIVIC SAFETY NETWORK'
  }
];

// ============================================================================
// ANIMATED COUNTER HOOK
// ============================================================================

function useSmoothCounter(target: number | undefined, duration = 650, active = false) {
  const [val, setVal] = useState<number>(0);
  const prevTargetRef = useRef<number>(0);

  useEffect(() => {
    if (!active || target === undefined) {
      setVal(0);
      prevTargetRef.current = 0;
      return;
    }

    const startVal = 0;
    const diff = target - startVal;
    const startTime = performance.now();
    let animId: number;

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duration);
      // easeOutExpo
      const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const current = Math.round(startVal + diff * ease);
      setVal(current);

      if (progress < 1) {
        animId = requestAnimationFrame(tick);
      } else {
        prevTargetRef.current = target;
      }
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [target, duration, active]);

  return val;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function HowYatriSetuWorks() {
  const [activeChapter, setActiveChapter] = useState<number>(0);
  const [mouseParallax, setMouseParallax] = useState({ x: 0, y: 0 });
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  const containerRef = useRef<HTMLElement>(null);
  const stickyRef = useRef<HTMLDivElement>(null);
  const chapterRefs = useRef<(HTMLDivElement | null)[]>([]);

  const isInView = useInView(containerRef, { once: true, amount: 0.15 });

  // Detect reduced motion preferences
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
      setIsReducedMotion(mq.matches);
      const handler = (e: MediaQueryListEvent) => setIsReducedMotion(e.matches);
      mq.addEventListener('change', handler);
      return () => mq.removeEventListener('change', handler);
    }
  }, []);

  // Desktop Mouse Parallax (6-10px max, disabled on touch/reduced motion)
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (isReducedMotion || !stickyRef.current) return;
    if (typeof window !== 'undefined' && window.matchMedia && !window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      return;
    }
    const rect = stickyRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 16; // -8 to +8px
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 16;
    setMouseParallax({ x, y });
  }, [isReducedMotion]);

  const handleMouseLeave = useCallback(() => {
    setMouseParallax({ x: 0, y: 0 });
  }, []);

  // Scroll Synchronization via IntersectionObserver
  useEffect(() => {
    const observers: IntersectionObserver[] = [];
    chapterRefs.current.forEach((el, index) => {
      if (!el) return;
      const obs = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setActiveChapter(index);
            }
          });
        },
        {
          rootMargin: '-25% 0px -45% 0px',
          threshold: 0.1
        }
      );
      obs.observe(el);
      observers.push(obs);
    });

    return () => {
      observers.forEach((obs) => obs.disconnect());
    };
  }, []);

  // Smooth scroll to chapter when clicking navigation
  const scrollToChapter = (idx: number) => {
    const el = chapterRefs.current[idx];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const current = FEATURE_CHAPTERS[activeChapter];
  const animatedScore = useSmoothCounter(current.metricValue, 650, true);

  return (
    <section
      ref={containerRef}
      className="relative w-full bg-[#0C0F14] text-white py-24 sm:py-32 overflow-hidden border-t border-stone-800/80"
      aria-label="How Yatri Setu Works — The Journey"
    >
      {/* Background ambient lighting and subtle texture */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,rgba(245,158,11,0.06),transparent)] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(#ffffff_0.5px,transparent_0.5px)] opacity-[0.025] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* ==================================================================== */}
        {/* SECTION HEADER (Large, Editorial, Premium)                           */}
        {/* ==================================================================== */}
        <div className="max-w-4xl mb-14 sm:mb-20">
          <motion.div
            initial={isReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center gap-2 mb-4"
          >
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span className="text-xs font-mono font-bold tracking-widest uppercase text-amber-400">
              THE YATRI SETU JOURNEY
            </span>
          </motion.div>

          <motion.h2
            initial={isReducedMotion ? {} : { opacity: 0, y: 24 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.06] text-white uppercase"
          >
            FROM DESTINATION PRESSURE
            <br />
            <span className="font-serif italic font-normal text-amber-200/90 lowercase text-3xl sm:text-5xl lg:text-6xl">
              to a better journey.
            </span>
          </motion.h2>

          <motion.p
            initial={isReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-base sm:text-lg text-stone-300 mt-4 leading-relaxed font-normal max-w-2xl text-balance"
          >
            Yatri Setu connects destination intelligence, smarter alternatives, local hosts and traveler safety into one continuous travel journey.
          </motion.p>
        </div>

        {/* ==================================================================== */}
        {/* FEATURE NAVIGATION / JOURNEY CONTROL BAR (5 Cards)                   */}
        {/* ==================================================================== */}
        <div className="mb-16 lg:mb-24">
          {/* Mobile horizontal scroll / Desktop 5-column layout */}
          <div className="flex lg:grid lg:grid-cols-5 gap-3 overflow-x-auto pb-4 lg:pb-0 scrollbar-none no-scrollbar -mx-4 px-4 sm:mx-0 sm:px-0">
            {FEATURE_CHAPTERS.map((f, idx) => {
              const isActive = activeChapter === idx;

              return (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => scrollToChapter(idx)}
                  className={cn(
                    'shrink-0 w-[240px] sm:w-[260px] lg:w-auto p-4 sm:p-5 rounded-2xl border text-left transition-all duration-400 ease-out flex flex-col justify-between select-none cursor-pointer',
                    isActive
                      ? 'bg-amber-500/10 border-amber-400/90 shadow-xl shadow-amber-500/5 ring-1 ring-amber-400/40 -translate-y-1'
                      : 'bg-stone-900/60 border-stone-800/90 hover:bg-stone-900 hover:border-stone-700 text-stone-400'
                  )}
                >
                  <div className="w-full">
                    {/* Top Row: Number + Badge */}
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <span
                        className={cn(
                          'text-2xl font-black font-mono tracking-tight',
                          isActive ? 'text-amber-400' : 'text-stone-500'
                        )}
                      >
                        {f.step}
                      </span>
                      <span
                        className={cn(
                          'text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase tracking-wider',
                          isActive
                            ? 'bg-amber-400/20 text-amber-200 border border-amber-400/40'
                            : 'bg-white/5 text-stone-400 border border-white/5'
                        )}
                      >
                        {f.badge}
                      </span>
                    </div>

                    {/* Feature Title */}
                    <h3
                      className={cn(
                        'text-xs sm:text-sm font-bold tracking-tight leading-snug transition-colors',
                        isActive ? 'text-white' : 'text-stone-300'
                      )}
                    >
                      {f.navTitle}
                    </h3>
                  </div>

                  {/* Active Indicator Bar */}
                  <div className="w-full mt-4 h-[2px] rounded-full overflow-hidden bg-stone-800">
                    <div
                      className={cn(
                        'h-full transition-all duration-500',
                        isActive ? 'w-full bg-amber-400' : 'w-0'
                      )}
                    />
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* ==================================================================== */}
        {/* MAIN STORY EXPERIENCE (Sticky Visual Left + Scrolling Story Right)   */}
        {/* ==================================================================== */}
        <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-start">
          
          {/* ------------------------------------------------------------------ */}
          {/* LEFT: STICKY CINEMATIC VISUAL (~55% Desktop Width)                */}
          {/* ------------------------------------------------------------------ */}
          <div className="lg:col-span-7 hidden lg:block sticky top-24 self-start">
            <div
              ref={stickyRef}
              onMouseMove={handleMouseMove}
              onMouseLeave={handleMouseLeave}
              className="relative w-full h-[640px] rounded-3xl overflow-hidden border border-stone-800 shadow-2xl bg-stone-950 flex flex-col justify-between p-8 select-none"
            >
              {/* LAYER 1 & 2: Background Cinematic Photography with Parallax */}
              <div className="absolute inset-0 overflow-hidden">
                <AnimatePresence mode="wait">
                  {activeChapter === 0 && (
                    <motion.img
                      key="darjeeling-bottleneck"
                      src="https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1600&q=85"
                      alt="Darjeeling ridge congested corridor"
                      initial={{ opacity: 0, scale: 1.06 }}
                      animate={{ opacity: 1, scale: 1.02 }}
                      exit={{ opacity: 0, scale: 1 }}
                      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                      style={{
                        transform: `translate3d(${mouseParallax.x}px, ${mouseParallax.y}px, 0) scale(1.02)`,
                        transition: 'transform 0.15s ease-out'
                      }}
                      className="w-full h-full object-cover filter brightness-[0.82]"
                    />
                  )}
                  {activeChapter === 1 && (
                    <motion.img
                      key="kalimpong-alternative"
                      src="https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1600&q=85"
                      alt="Kalimpong serene orchid ridge"
                      initial={{ opacity: 0, scale: 1.06 }}
                      animate={{ opacity: 1, scale: 1.02 }}
                      exit={{ opacity: 0, scale: 1 }}
                      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                      style={{
                        transform: `translate3d(${mouseParallax.x}px, ${mouseParallax.y}px, 0) scale(1.02)`,
                        transition: 'transform 0.15s ease-out'
                      }}
                      className="w-full h-full object-cover filter brightness-[0.85]"
                    />
                  )}
                  {activeChapter === 2 && (
                    <motion.img
                      key="itinerary-path"
                      src="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=85"
                      alt="Himalayan mountain trails"
                      initial={{ opacity: 0, scale: 1.06 }}
                      animate={{ opacity: 1, scale: 1.02 }}
                      exit={{ opacity: 0, scale: 1 }}
                      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                      style={{
                        transform: `translate3d(${mouseParallax.x}px, ${mouseParallax.y}px, 0) scale(1.02)`,
                        transition: 'transform 0.15s ease-out'
                      }}
                      className="w-full h-full object-cover filter brightness-[0.82]"
                    />
                  )}
                  {activeChapter === 3 && (
                    <motion.img
                      key="panchayat-homestay"
                      src="https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=1600&q=85"
                      alt="Village homestay wooden sanctuary"
                      initial={{ opacity: 0, scale: 1.06 }}
                      animate={{ opacity: 1, scale: 1.02 }}
                      exit={{ opacity: 0, scale: 1 }}
                      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                      style={{
                        transform: `translate3d(${mouseParallax.x}px, ${mouseParallax.y}px, 0) scale(1.02)`,
                        transition: 'transform 0.15s ease-out'
                      }}
                      className="w-full h-full object-cover filter brightness-[0.80]"
                    />
                  )}
                  {activeChapter === 4 && (
                    <motion.img
                      key="safety-guardian"
                      src="https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1600&q=85"
                      alt="Misty protected pine valley"
                      initial={{ opacity: 0, scale: 1.06 }}
                      animate={{ opacity: 1, scale: 1.02 }}
                      exit={{ opacity: 0, scale: 1 }}
                      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                      style={{
                        transform: `translate3d(${mouseParallax.x}px, ${mouseParallax.y}px, 0) scale(1.02)`,
                        transition: 'transform 0.15s ease-out'
                      }}
                      className="w-full h-full object-cover filter brightness-[0.82]"
                    />
                  )}
                </AnimatePresence>

                {/* Layered gradients for legibility */}
                <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/60 to-stone-950/30" />
                <div className="absolute inset-0 bg-gradient-to-r from-stone-950/80 via-transparent to-stone-950/50" />
              </div>

              {/* LAYER 3: Chapter Header Stamp & Scroll Progress Bar */}
              <div className="relative z-10 flex items-start justify-between">
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/55 backdrop-blur-md border border-white/10 text-[11px] font-mono tracking-widest uppercase text-stone-300">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  <span>PHASE {current.step} OF 05</span>
                </div>

                {/* Subtle Vertical Progress Indicator (01 ● │ 02 ○ ...) */}
                <div className="flex flex-col items-center gap-1 bg-black/55 backdrop-blur-md px-2.5 py-2 rounded-2xl border border-white/10 text-[10px] font-mono">
                  {FEATURE_CHAPTERS.map((ch, idx) => (
                    <React.Fragment key={ch.id}>
                      <button
                        type="button"
                        onClick={() => scrollToChapter(idx)}
                        className={cn(
                          'flex items-center gap-1.5 transition-colors cursor-pointer py-0.5',
                          activeChapter === idx ? 'text-amber-300 font-bold' : 'text-stone-500 hover:text-stone-300'
                        )}
                      >
                        <span>{ch.step}</span>
                        <span
                          className={cn(
                            'w-2 h-2 rounded-full transition-all duration-300',
                            activeChapter === idx
                              ? 'bg-amber-400 ring-2 ring-amber-400/40 scale-125'
                              : 'bg-stone-700'
                          )}
                        />
                      </button>
                      {idx < FEATURE_CHAPTERS.length - 1 && (
                        <span className="w-[1px] h-2 bg-stone-800" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* LAYER 4: Continuous Evolving Intelligence Transformations */}
              <div className="relative z-10 mt-auto pt-6">
                <AnimatePresence mode="wait">
                  
                  {/* CHAPTER 01 TRANSFORMATION: DETECT BOTTLENECK */}
                  {activeChapter === 0 && (
                    <motion.div
                      key="vis-01"
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -12 }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      className="space-y-4"
                    >
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-mono font-bold">
                        <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                        <span>SATURATION ALERT DETECTED</span>
                      </div>

                      <div>
                        <h4 className="text-3xl font-extrabold uppercase tracking-tight text-white">
                          Darjeeling Ridge
                        </h4>
                        <p className="text-xs font-mono text-stone-300 uppercase tracking-wider mt-0.5">
                          Hill Cart Road Corridor · Eastern Himalayas
                        </p>
                      </div>

                      {/* Barometer & Metric Display */}
                      <div className="p-4 rounded-2xl bg-black/60 backdrop-blur-md border border-white/10 flex items-center justify-between gap-4">
                        <div>
                          <span className="text-[10px] font-mono uppercase text-stone-400 block font-semibold">
                            CROWD CONGESTION LEVEL
                          </span>
                          <span className="text-3xl font-mono font-black text-rose-400 mt-1 block">
                            {animatedScore} / 100
                          </span>
                          <span className="text-[10px] font-mono text-stone-300">
                            Severe peak holiday traffic delay
                          </span>
                        </div>

                        <div className="text-right">
                          <span className="text-[10px] font-mono uppercase text-stone-400 block font-semibold">
                            RECOMMENDATION
                          </span>
                          <span className="text-xs font-mono font-bold text-amber-300 mt-1 block uppercase">
                            Divert to Sister Ridge
                          </span>
                          <span className="text-[10px] text-stone-400">
                            6-Factor capacity trigger
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* CHAPTER 02 TRANSFORMATION: REDIRECT & CAPACITY MATCH */}
                  {activeChapter === 1 && (
                    <motion.div
                      key="vis-02"
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -12 }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      className="space-y-4"
                    >
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-mono font-bold">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>AI CAPACITY MATCH FOUND</span>
                      </div>

                      {/* Receding vs Advancing Destinations */}
                      <div className="grid grid-cols-2 gap-3 items-center">
                        {/* Crowded (Receding) */}
                        <div className="p-3.5 rounded-xl bg-black/40 border border-white/5 opacity-50 scale-95 transition-all">
                          <span className="text-[9px] font-mono uppercase text-rose-400 block font-bold">
                            OVERBURDENED
                          </span>
                          <h5 className="text-sm font-bold text-stone-300 uppercase">Darjeeling</h5>
                          <span className="text-xs font-mono text-stone-400 mt-1 block">
                            88 / 100 Pressure
                          </span>
                        </div>

                        {/* Better Fit Alternative (Advancing) */}
                        <div className="p-4 rounded-xl bg-amber-500/15 border border-amber-400/80 shadow-lg ring-1 ring-amber-400/30 scale-100 transition-all">
                          <span className="text-[9px] font-mono uppercase text-amber-300 block font-bold">
                            OPTIMAL SANCTUARY
                          </span>
                          <h5 className="text-lg font-extrabold text-white uppercase">Kalimpong</h5>
                          <div className="flex items-center justify-between text-xs font-mono text-emerald-300 mt-1">
                            <span>42 / 100 Flow</span>
                            <span className="font-bold">{animatedScore}% Match</span>
                          </div>
                        </div>
                      </div>

                      <div className="p-3 rounded-xl bg-black/50 backdrop-blur-md border border-white/10 text-xs font-mono text-stone-300 flex items-center justify-between">
                        <span>ESTIMATED DAILY SAVINGS: 42%</span>
                        <span className="text-amber-400 font-bold">ZERO QUEUES</span>
                      </div>
                    </motion.div>
                  )}

                  {/* CHAPTER 03 TRANSFORMATION: ADAPTIVE ITINERARY FLOW */}
                  {activeChapter === 2 && (
                    <motion.div
                      key="vis-03"
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -12 }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      className="space-y-4"
                    >
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-bold">
                        <Compass className="w-3.5 h-3.5" />
                        <span>FLOW-OPTIMIZED EXPEDITION</span>
                      </div>

                      {/* Flowing Journey Path Waypoints */}
                      <div className="p-4 rounded-2xl bg-black/60 backdrop-blur-md border border-white/10 space-y-3 font-mono">
                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-full bg-amber-400 text-stone-950 font-black text-xs flex items-center justify-center">
                            1
                          </span>
                          <div>
                            <span className="text-xs font-bold text-white block">DAY 01 · 11:30 AM · ARRIVE RIDGE</span>
                            <span className="text-[10px] text-stone-400">Panchayat homestay check-in avoiding noon highway jam</span>
                          </div>
                        </div>

                        <div className="w-[1px] h-3 bg-amber-400/60 ml-3" />

                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-full bg-amber-400 text-stone-950 font-black text-xs flex items-center justify-center">
                            2
                          </span>
                          <div>
                            <span className="text-xs font-bold text-white block">DAY 02 · 08:30 AM · BOTANICAL DISCOVERY</span>
                            <span className="text-[10px] text-stone-400">Pine View Orchid Sanctuary during zero-footfall window</span>
                          </div>
                        </div>

                        <div className="w-[1px] h-3 bg-amber-400/60 ml-3" />

                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-full bg-amber-400 text-stone-950 font-black text-xs flex items-center justify-center">
                            3
                          </span>
                          <div>
                            <span className="text-xs font-bold text-white block">DAY 03 · 05:45 AM · KANCHENJUNGA SUNRISE</span>
                            <span className="text-[10px] text-stone-400">Rishop 360° ridge without 3-hour Tiger Hill vehicle queue</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* CHAPTER 04 TRANSFORMATION: PANCHAYAT HOST BOOKING */}
                  {activeChapter === 3 && (
                    <motion.div
                      key="vis-04"
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -12 }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      className="space-y-4"
                    >
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-bold">
                        <Leaf className="w-3.5 h-3.5" />
                        <span>VERIFIED PANCHAYAT LEDGER</span>
                      </div>

                      <div>
                        <h4 className="text-2xl font-extrabold uppercase tracking-tight text-white">
                          Pineview Orchid Cottage
                        </h4>
                        <p className="text-xs font-mono text-stone-300 uppercase mt-0.5">
                          Upper Cart Road · Hosted by Gurung Family
                        </p>
                      </div>

                      {/* 90% Host Share Metric Highlight */}
                      <div className="p-4 rounded-2xl bg-black/60 backdrop-blur-md border border-white/10 flex items-center justify-between gap-4">
                        <div>
                          <span className="text-[10px] font-mono uppercase text-stone-400 block font-semibold">
                            DIRECT SETTLEMENT SHARE
                          </span>
                          <span className="text-3xl font-mono font-black text-emerald-400 mt-1 block">
                            {animatedScore}% DIRECT
                          </span>
                          <span className="text-[10px] font-mono text-stone-300">
                            Transparent village community split
                          </span>
                        </div>

                        <div className="text-right">
                          <span className="text-[10px] font-mono uppercase text-stone-400 block font-semibold">
                            ECO CREDITS
                          </span>
                          <span className="text-xs font-mono font-bold text-amber-300 mt-1 block">
                            +120 GREEN COINS
                          </span>
                          <span className="text-[10px] text-stone-400">
                            Responsible travel reward
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* CHAPTER 05 TRANSFORMATION: YATRI MITRA SAFETY GUARDIAN */}
                  {activeChapter === 4 && (
                    <motion.div
                      key="vis-05"
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -12 }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      className="space-y-4"
                    >
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-mono font-bold">
                        <RadioTower className="w-3.5 h-3.5" />
                        <span>ACTIVE TELEMETRY GUARDIAN</span>
                      </div>

                      <div>
                        <h4 className="text-2xl font-extrabold uppercase tracking-tight text-white">
                          Yatri Mitra Emergency Net
                        </h4>
                        <p className="text-xs font-mono text-stone-300 uppercase mt-0.5">
                          High-Altitude Safety Infrastructure
                        </p>
                      </div>

                      <div className="p-4 rounded-2xl bg-black/60 backdrop-blur-md border border-white/10 space-y-2.5 font-mono text-xs">
                        <div className="flex items-center justify-between">
                          <span className="text-stone-400">NATIONAL 112 DISPATCH:</span>
                          <span className="text-emerald-400 font-bold">ONLINE & SYNCED</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-stone-400">GPS TELEMETRY (DEMO):</span>
                          <span className="text-white font-bold">27.0594° N, 88.2625° E</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-stone-400">LOCAL VOLUNTEER MESH:</span>
                          <span className="text-amber-300 font-bold">4 Wardens Within 1.4km</span>
                        </div>
                      </div>
                    </motion.div>
                  )}

                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* ------------------------------------------------------------------ */}
          {/* RIGHT: SCROLLING EDITORIAL STORY (5 Chapters, ~45% Desktop Width)  */}
          {/* ------------------------------------------------------------------ */}
          <div className="lg:col-span-5 flex flex-col space-y-24 sm:space-y-36 pb-12">
            {FEATURE_CHAPTERS.map((f, idx) => {
              const isActive = activeChapter === idx;

              return (
                <div
                  key={f.id}
                  ref={(el) => {
                    chapterRefs.current[idx] = el;
                  }}
                  className={cn(
                    'transition-opacity duration-500 ease-out flex flex-col justify-center min-h-[50vh] lg:min-h-[70vh]',
                    isActive ? 'opacity-100' : 'opacity-35'
                  )}
                >
                  {/* Step Number & Technical Label */}
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-4xl sm:text-5xl font-mono font-black text-amber-400">
                      {f.step}
                    </span>
                    <span className="text-[10px] font-mono tracking-widest uppercase text-stone-400 font-semibold bg-white/5 px-2.5 py-1 rounded-md border border-white/5">
                      {f.technicalLabel}
                    </span>
                  </div>

                  {/* Chapter Heading */}
                  <h3 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold uppercase tracking-tight text-white leading-tight">
                    {f.chapterTitle}
                  </h3>

                  {/* Story Lead Sentence */}
                  <p className="text-base sm:text-lg text-amber-200/90 font-serif italic mt-3 leading-snug">
                    {f.storyHeading}
                  </p>

                  {/* Story Body Copy */}
                  <div className="mt-4 space-y-3 text-sm sm:text-base text-stone-300 font-normal leading-relaxed">
                    <p>{f.storyLead}</p>
                    <p className="text-xs sm:text-sm text-stone-400 font-light">{f.storyDetail}</p>
                  </div>

                  {/* Action Link & Direct Launch Button */}
                  <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between gap-4">
                    <Link
                      href={f.actionUrl}
                      className="inline-flex items-center gap-2 text-xs font-bold font-mono uppercase tracking-wider text-amber-400 hover:text-amber-300 transition-colors group"
                    >
                      <span>{f.actionText}</span>
                      <ArrowRight className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-1" />
                    </Link>

                    {/* Numeric Tag */}
                    <span className="text-[10px] font-mono text-stone-500 uppercase tracking-widest hidden sm:inline">
                      CHAPTER {f.step} OF 05
                    </span>
                  </div>

                  {/* Mobile-Only Inline Visual Transformation Block */}
                  <div className="mt-6 lg:hidden p-5 rounded-2xl bg-stone-900 border border-stone-800 text-xs font-mono space-y-2">
                    <div className="flex items-center justify-between text-amber-400 font-bold">
                      <span>{f.metricLabel}</span>
                      <span>
                        {f.metricValue}
                        {f.metricSuffix}
                      </span>
                    </div>
                    <p className="text-[11px] text-stone-400 font-sans">{f.metricSub}</p>
                  </div>
                </div>
              );
            })}
          </div>

        </div>

        {/* ==================================================================== */}
        {/* FUTURE-READY CINEMATIC CLOSING CTA                                   */}
        {/* ==================================================================== */}
        <div className="mt-28 sm:mt-36 pt-12 border-t border-stone-800/80">
          <div className="relative rounded-3xl overflow-hidden border border-stone-800 bg-stone-900/80 p-8 sm:p-14 lg:p-20 text-center shadow-2xl">
            {/* Background Himalayan visual with slow zoom */}
            <div className="absolute inset-0 overflow-hidden">
              <img
                src="/hero-himalaya.jpg"
                alt="End of journey Himalayan landscape"
                className="w-full h-full object-cover filter brightness-[0.35] scale-105"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/70 to-stone-950/40" />
            </div>

            {/* Content Container */}
            <div className="relative z-10 max-w-3xl mx-auto space-y-6">
              {/* Journey Convergence Trail */}
              <div className="inline-flex flex-wrap items-center justify-center gap-2 text-[10px] sm:text-xs font-mono font-bold tracking-widest uppercase text-amber-300/90 bg-black/60 px-4 py-2 rounded-full border border-amber-400/30 shadow-md">
                <span>DETECT</span>
                <span className="text-stone-500">→</span>
                <span>MATCH</span>
                <span className="text-stone-500">→</span>
                <span>PLAN</span>
                <span className="text-stone-500">→</span>
                <span>CONNECT</span>
                <span className="text-stone-500">→</span>
                <span>TRAVEL SAFELY</span>
              </div>

              {/* Headline */}
              <h3 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight uppercase">
                READY TO TRAVEL DIFFERENTLY?
              </h3>

              {/* Supporting Text */}
              <p className="text-sm sm:text-base text-stone-300 max-w-xl mx-auto leading-relaxed">
                Choose a destination, understand the pressure, and discover a journey that fits you.
              </p>

              {/* Action Buttons */}
              <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
                <Link
                  href="/destinations"
                  className="px-8 py-3.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-stone-950 font-extrabold text-xs sm:text-sm tracking-wider uppercase inline-flex items-center gap-2 transition-all shadow-lg hover:shadow-amber-400/20"
                >
                  <span>EXPLORE DESTINATIONS</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>

                <Link
                  href="/itinerary"
                  className="px-7 py-3.5 rounded-xl bg-stone-800/80 hover:bg-stone-700/80 text-white font-bold text-xs sm:text-sm tracking-wider uppercase inline-flex items-center gap-2 border border-stone-700 hover:border-amber-400/50 transition-all backdrop-blur-sm"
                >
                  <span>PLAN MY JOURNEY</span>
                  <ArrowUpRight className="w-4 h-4" />
                </Link>
              </div>

              {/* Trust & Architecture Strip */}
              <div className="pt-8 border-t border-white/10 flex flex-wrap items-center justify-center gap-6 text-[10px] font-mono uppercase text-stone-400">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                  <span>SMART INDIA HACKATHON 2026</span>
                </div>
                <span className="text-stone-700 hidden sm:inline">•</span>
                <div className="flex items-center gap-1.5">
                  <Leaf className="w-3.5 h-3.5 text-emerald-400" />
                  <span>REGENERATIVE TOURISM ARCHITECTURE</span>
                </div>
                <span className="text-stone-700 hidden sm:inline">•</span>
                <div className="flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5 text-sky-400" />
                  <span>COMMUNITY-VERIFIED HOMESTAYS</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
