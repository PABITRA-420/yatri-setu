'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  ArrowUpRight,
  Sparkles,
  Shield,
  MapPin,
  Clock,
  CheckCircle2,
  Leaf,
  Users,
  AlertTriangle,
  Compass,
  Radio,
  Coins,
  TrendingDown
} from 'lucide-react';
import { motion, useInView, useScroll, useTransform, useSpring } from 'motion/react';
import { cn } from '@/lib/utils';

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
  image: string;
  watermark: string;
  floatingPill1: { icon: string; text: string };
  floatingPill2: { icon: string; text: string };
  floatingPill3: { icon: string; text: string };
  textParallaxBadge: { icon: string; label: string; val: string };
  accentMetric: { label: string; stat: string; sub: string };
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
    technicalLabel: '6-FACTOR DECONGESTION TELEMETRY',
    image: '/hero-himalaya.jpg',
    watermark: '01 DECONGESTION',
    floatingPill1: { icon: '📍', text: 'Tiger Hill Saturation • 8,482 ft' },
    floatingPill2: { icon: '⚠️', text: 'Hill Cart Road Corridor Delay' },
    floatingPill3: { icon: '📊', text: '+74 min gridlock • Severe Peak Saturation' },
    textParallaxBadge: { icon: '⚡', label: 'LIVE SENSOR SATURATION', val: '88% CAPACITY EXCEEDED' },
    accentMetric: {
      label: 'TIGER HILL BOTTLENECK TELEMETRY',
      stat: '88 / 100',
      sub: 'Multi-factor choke point alert triggered along Hill Cart Road corridor'
    }
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
    technicalLabel: 'CAPACITY-BALANCED REDIRECTION',
    image: '/experience_bg.jpg',
    watermark: '02 AFFINITY',
    floatingPill1: { icon: '🏔️', text: '360° Kanchenjunga • Zero Queues' },
    floatingPill2: { icon: '💰', text: '42% Lower Daily Tariff • Rural Direct' },
    floatingPill3: { icon: '✨', text: 'Rishop Ridge Sanctuary • 87% Experiential Match' },
    textParallaxBadge: { icon: '🌿', label: 'AFFINITY REDIRECTION', val: 'KALIMPONG RIDGE • 87% MATCH' },
    accentMetric: {
      label: 'ECOLOGICAL SISTER SANCTUARY',
      stat: '87% MATCH',
      sub: '42% lower daily tariff · Zero queues · Preserves fragile ridge ecosystems'
    }
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
    technicalLabel: 'TEMPORAL FLOW OPTIMIZATION',
    image: '/demo_flow_bg.jpg',
    watermark: '03 EXPEDITION',
    floatingPill1: { icon: '⏰', text: '05:45 AM Off-Peak Sunrise Window' },
    floatingPill2: { icon: '🚶', text: 'Lepcha Craft Trail • Staggered Flow' },
    floatingPill3: { icon: '⏳', text: '-65% Peak Wait Times • Algorithmic Pacing' },
    textParallaxBadge: { icon: '⏱️', label: 'TEMPORAL FLOW PACING', val: '05:45 AM OFF-PEAK STAGGERING' },
    accentMetric: {
      label: 'TEMPORAL QUEUE ELIMINATION',
      stat: '-65% WAIT',
      sub: 'Dynamically shifts excursion windows 45 mins ahead of mass tourist buses'
    }
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
    technicalLabel: 'COMMUNITY LEDGER SETTLEMENT',
    image: '/sanctuaries_bg.jpg',
    watermark: '04 COMMUNITY',
    floatingPill1: { icon: '🏡', text: 'Gurung Family Unit #14 • Panchayat Verified' },
    floatingPill2: { icon: '🪙', text: '+120 Green Coins • Village Fund' },
    floatingPill3: { icon: '🌱', text: 'Gram Panchayat Eco-Audit #WB-409 • Verified' },
    textParallaxBadge: { icon: '🤝', label: 'COMMUNITY LEDGER', val: '90% DIRECT TO GURUNG COTTAGE' },
    accentMetric: {
      label: 'DIRECT HOST REVENUE SHARE',
      stat: '90% DIRECT',
      sub: 'Zero intermediary cut · Funds local youth guides and village conservation'
    }
  },
  {
    id: 'emergency-net',
    step: '05',
    badge: 'National 112 & GPS',
    navTitle: 'Emergency SOS Net',
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
    technicalLabel: 'CIVIC SAFETY NETWORK',
    image: '/image2.png',
    watermark: '05 CIVIC SAFETY',
    floatingPill1: { icon: '📡', text: '4 Yatri Mitras within 1.4km' },
    floatingPill2: { icon: '🛰️', text: 'GPS 27.0594° N, 88.2625° E • Cached Fix' },
    floatingPill3: { icon: '🚨', text: 'National 112 Integration • Satellite Relay' },
    textParallaxBadge: { icon: '🛡️', label: 'CIVIC SAFETY MESH', val: '4 WARDENS WITHIN 1.4 KM' },
    accentMetric: {
      label: 'RAPID DISPATCH & MESH SATELLITE',
      stat: '112 READY',
      sub: 'Real-time GPS coordinate caching with local community wardens & police dispatch'
    }
  }
];

// ============================================================================
// ANIMATED COUNTER HOOK
// ============================================================================

function useSmoothCounter(target: number | undefined, duration = 750, active = false) {
  const [val, setVal] = useState<number>(0);

  useEffect(() => {
    if (!active || target === undefined) {
      return;
    }

    const startVal = 0;
    const diff = target - startVal;
    const startTime = performance.now();
    let animId: number;

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duration);
      const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const current = Math.round(startVal + diff * ease);
      setVal(current);

      if (progress < 1) {
        animId = requestAnimationFrame(tick);
      }
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [target, duration, active]);

  return val;
}

// ============================================================================
// CHAPTER ROW COMPONENT WITH MULTI-LAYER PARALLAX (IMAGE, TEXT, AND WATERMARKS)
// ============================================================================

interface ChapterRowProps {
  chapter: FeatureChapter;
  index: number;
  onVisible: (idx: number) => void;
}

function ChapterRow({ chapter, index, onVisible }: ChapterRowProps) {
  const rowRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(rowRef, { amount: 0.25 });
  const [mouseParallax, setMouseParallax] = useState({ x: 0, y: 0 });

  // SCROLL-DRIVEN DYNAMIC MULTI-LAYER PARALLAX
  const { scrollYProgress } = useScroll({
    target: rowRef,
    offset: ['start end', 'end start']
  });

  const smoothProgress = useSpring(scrollYProgress, { stiffness: 90, damping: 20, mass: 0.18 });

  // 1. Image vertical parallax drift inside the container
  const imageY = useTransform(smoothProgress, [0, 1], ['-12%', '12%']);
  const imageScale = useTransform(smoothProgress, [0, 0.5, 1], [1.14, 1.05, 1.14]);

  // 2. Large decorative ghost typography watermark floats with counter-motion
  const watermarkY = useTransform(smoothProgress, [0, 1], ['-45px', '45px']);

  // 3. Floating telemetry badges layered across the image glide with differential parallax
  const floatingBadge1Y = useTransform(smoothProgress, [0, 1], ['32px', '-32px']);
  const floatingBadge2Y = useTransform(smoothProgress, [0, 1], ['-26px', '26px']);
  const floatingBadge3Y = useTransform(smoothProgress, [0, 1], ['42px', '-18px']);

  // 4. Parallax Text beside the images (Chapters 1, 2, 3, 4, 5):
  // - Large Step numeral (01, 02, 03, 04, 05) glides with its own vertical parallax offset
  const stepNumY = useTransform(smoothProgress, [0, 1], ['-28px', '28px']);
  // - Heading and editorial quote glide with subtle counter-parallax
  const headingY = useTransform(smoothProgress, [0, 1], ['14px', '-14px']);
  // - Floating highlight badge beside the chapter text glides at independent speed
  const textBadgeY = useTransform(smoothProgress, [0, 1], ['-22px', '22px']);
  // - Accent metric card glides with subtle elevation
  const textAccentY = useTransform(smoothProgress, [0, 1], ['18px', '-18px']);
  // - Right column overall smooth glide
  const textColY = useTransform(smoothProgress, [0, 1], ['16px', '-16px']);

  useEffect(() => {
    if (isInView) {
      onVisible(index);
    }
  }, [isInView, index, onVisible]);

  // Smooth animated counter for this specific chapter
  const counterValue = useSmoothCounter(chapter.metricValue, 800, isInView);

  // Mouse Parallax 3D tilt calculations
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 16;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 16;
    setMouseParallax({ x, y });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setMouseParallax({ x: 0, y: 0 });
  }, []);

  return (
    <div
      id={chapter.id}
      ref={rowRef}
      className="scroll-mt-32 py-8 sm:py-12 lg:py-14 border-b border-stone-800/60 last:border-b-0"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-14 items-center">
        
        {/* ------------------------------------------------------------------ */}
        {/* VISUAL SHOWCASE CARD WITH MULTI-LAYER PARALLAX (LEFT ~58%)         */}
        {/* ------------------------------------------------------------------ */}
        <div className="lg:col-span-7 order-2 lg:order-1">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0.4, y: 15 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className="group relative w-full h-[480px] sm:h-[540px] lg:h-[600px] rounded-3xl overflow-hidden border border-white/10 shadow-2xl bg-stone-950 flex flex-col justify-between p-6 sm:p-8 select-none transition-all duration-300 hover:border-amber-400/40 hover:shadow-amber-500/10"
            style={{ perspective: 1000 }}
          >
            {/* 1. PARALLAX BACKGROUND IMAGE */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <motion.img
                src={chapter.image}
                alt={chapter.chapterTitle}
                loading="eager"
                decoding="async"
                style={{
                  y: imageY,
                  scale: imageScale,
                  x: mouseParallax.x * -0.6,
                  transition: 'x 0.25s ease-out'
                }}
                className="w-full h-full object-cover filter brightness-[0.78] group-hover:brightness-[0.84] transition-all duration-700"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/60 to-stone-950/25" />
              <div className="absolute inset-0 bg-gradient-to-r from-stone-950/85 via-stone-950/30 to-transparent" />
            </div>

            {/* 2. PARALLAX FLOATING GHOST TYPOGRAPHY WATERMARK */}
            <motion.div
              style={{
                y: watermarkY,
                x: mouseParallax.x * 0.5,
                transition: 'x 0.25s ease-out'
              }}
              className="absolute top-1/3 left-6 right-6 pointer-events-none select-none z-10 opacity-[0.14] group-hover:opacity-[0.22] transition-opacity duration-500"
            >
              <span className="font-mono font-black text-5xl sm:text-7xl lg:text-8xl tracking-tighter uppercase text-white block leading-none">
                {chapter.watermark}
              </span>
            </motion.div>

            {/* 3. PARALLAX FLOATING TELEMETRY PILLS (ACTIVE OVER IMAGE) */}
            <div className="absolute inset-x-6 top-18 pointer-events-none z-15 flex flex-col items-end gap-2">
              {/* Floating Pill 1 (Glides with positive parallax) */}
              <motion.div
                style={{
                  y: floatingBadge1Y,
                  x: mouseParallax.x * 1.2,
                  transition: 'x 0.25s ease-out'
                }}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-[10px] sm:text-[11px] font-mono font-bold text-amber-200 shadow-xl"
              >
                <span>{chapter.floatingPill1.icon}</span>
                <span>{chapter.floatingPill1.text}</span>
              </motion.div>

              {/* Floating Pill 2 (Glides with counter parallax) */}
              <motion.div
                style={{
                  y: floatingBadge2Y,
                  x: mouseParallax.x * 0.9,
                  transition: 'x 0.25s ease-out'
                }}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-[10px] sm:text-[11px] font-mono font-bold text-emerald-200 shadow-xl"
              >
                <span>{chapter.floatingPill2.icon}</span>
                <span>{chapter.floatingPill2.text}</span>
              </motion.div>

              {/* Floating Pill 3 (Glides with tertiary parallax depth) */}
              <motion.div
                style={{
                  y: floatingBadge3Y,
                  x: mouseParallax.x * 1.4,
                  transition: 'x 0.25s ease-out'
                }}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/80 backdrop-blur-md border border-amber-400/30 text-[10px] sm:text-[11px] font-mono font-bold text-amber-300 shadow-xl"
              >
                <span>{chapter.floatingPill3.icon}</span>
                <span>{chapter.floatingPill3.text}</span>
              </motion.div>
            </div>

            {/* 4. TOP HUD BAR */}
            <div className="relative z-20 flex items-center justify-between pointer-events-auto">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/75 backdrop-blur-md border border-white/15 text-[11px] font-mono tracking-widest uppercase text-stone-200 shadow-md">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                <span>PHASE {chapter.step} OF 05</span>
              </div>

              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-black/75 backdrop-blur-md border border-white/15 text-[10px] font-mono font-bold uppercase tracking-wider text-amber-300 shadow-md">
                <span>{chapter.badge}</span>
              </div>
            </div>

            {/* 5. BOTTOM INTERACTIVE PANEL (CHAPTER SPECIFIC WITH GLASSMORPHISM) */}
            <div
              className="relative z-20 space-y-4 pointer-events-auto min-h-[220px] sm:min-h-[240px] flex flex-col justify-end"
              style={{
                transform: `translate3d(${mouseParallax.x * 0.8}px, ${mouseParallax.y * 0.8}px, 0)`,
                transition: 'transform 0.25s ease-out'
              }}
            >
              
              {/* SCENE 01: Bottleneck Alert */}
              {index === 0 && (
                <>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-mono font-bold">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                    <span>SATURATION ALERT DETECTED</span>
                  </div>

                  <div>
                    <h4 className="text-2xl sm:text-3xl font-extrabold uppercase tracking-tight text-white">
                      DARJEELING RIDGE
                    </h4>
                    <p className="text-xs font-mono text-stone-300 uppercase tracking-wider mt-1">
                      Hill Cart Road Corridor · Eastern Himalayas
                    </p>
                  </div>

                  <div className="p-4 sm:p-5 rounded-2xl bg-black/75 backdrop-blur-xl border border-white/15 flex items-center justify-between gap-4">
                    <div>
                      <span className="text-[10px] font-mono uppercase text-stone-400 block font-semibold tracking-wider">
                        CROWD CONGESTION LEVEL
                      </span>
                      <span className="text-3xl sm:text-4xl font-mono font-black text-rose-400 mt-1 block">
                        {counterValue} / 100
                      </span>
                      <span className="text-[10px] font-mono text-stone-300">
                        Severe peak holiday traffic delay risk
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] font-mono uppercase text-stone-400 block font-semibold tracking-wider">
                        RECOMMENDATION:
                      </span>
                      <span className="text-xs font-mono font-bold text-amber-300 mt-1 block uppercase">
                        DIVERT TO SISTER RIDGE
                      </span>
                      <span className="text-[10px] text-stone-400 block mt-0.5">
                        6-Factor capacity trigger
                      </span>
                    </div>
                  </div>
                </>
              )}

              {/* SCENE 02: AI Similarity & Capacity Match */}
              {index === 1 && (
                <>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-mono font-bold">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>CAPACITY-BALANCED REDIRECTION</span>
                  </div>

                  <div>
                    <h4 className="text-2xl sm:text-3xl font-extrabold uppercase tracking-tight text-white">
                      HIGH PRESSURE → SIMILAR ALTERNATIVE
                    </h4>
                    <p className="text-xs font-mono text-stone-300 uppercase tracking-wider mt-1">
                      Sister Sanctuary Ecological & Experiential Pairing
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="grid grid-cols-2 gap-3 items-center">
                      <div className="p-3.5 rounded-xl bg-black/65 backdrop-blur-md border border-rose-500/30">
                        <div className="flex items-center justify-between">
                          <span className="text-[9px] font-mono uppercase text-rose-400 font-bold tracking-wider">
                            DARJEELING
                          </span>
                          <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">
                            VERY HIGH
                          </span>
                        </div>
                        <span className="text-xl font-mono font-black text-rose-400 mt-0.5 block">
                          88 / 100
                        </span>
                        <span className="text-[10px] font-mono text-stone-400">
                          Saturated Ridge
                        </span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-amber-500/20 backdrop-blur-md border border-amber-400/80 shadow-lg ring-1 ring-amber-400/30">
                        <div className="flex items-center justify-between">
                          <span className="text-[9px] font-mono uppercase text-amber-300 font-bold tracking-wider">
                            KALIMPONG
                          </span>
                          <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                            MEDIUM
                          </span>
                        </div>
                        <span className="text-xl font-mono font-black text-emerald-400 mt-0.5 block">
                          42 / 100
                        </span>
                        <span className="text-[10px] font-mono text-amber-300 font-bold">
                          {counterValue}% SIMILAR
                        </span>
                      </div>
                    </div>

                    <div className="p-2.5 rounded-xl bg-black/65 backdrop-blur-md border border-white/10 text-xs font-mono text-stone-300 flex items-center justify-between">
                      <span className="text-stone-400">ECOLOGICALLY MATCHED RIDGE</span>
                      <span className="text-amber-400 font-bold">42% TARIFF SAVINGS · ZERO QUEUES</span>
                    </div>
                  </div>
                </>
              )}

              {/* SCENE 03: Adaptive Crowd-Smart Itinerary */}
              {index === 2 && (
                <>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-[10px] font-mono font-bold uppercase tracking-wider">
                      DAY-BY-DAY FLOW
                    </span>
                    <span className="px-2.5 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[10px] font-mono font-bold uppercase tracking-wider">
                      LOWER-PRESSURE WINDOW
                    </span>
                    <span className="px-2.5 py-1 rounded-full bg-sky-500/20 border border-sky-500/40 text-sky-300 text-[10px] font-mono font-bold uppercase tracking-wider">
                      LOCAL EXPERIENCE
                    </span>
                  </div>

                  <div>
                    <h4 className="text-2xl sm:text-3xl font-extrabold uppercase tracking-tight text-white">
                      ADAPTIVE CROWD-SMART ITINERARY
                    </h4>
                    <p className="text-xs font-mono text-stone-300 uppercase tracking-wider mt-1">
                      Editorial Flow Route & Temporal Pacing
                    </p>
                  </div>

                  <div className="p-4 sm:p-5 rounded-2xl bg-black/75 backdrop-blur-xl border border-white/15 space-y-2.5 font-mono">
                    <div>
                      <div className="flex items-center justify-between text-xs font-bold text-white mb-1">
                        <span className="text-amber-400">DAY 01 · ARRIVE</span>
                        <span className="text-[10px] text-stone-400 font-normal">11:30 AM</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-stone-300 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
                        <span>ARRIVAL</span>
                        <span className="text-amber-400/60">●────────●</span>
                        <span className="text-amber-300 font-bold">HOMESTAY</span>
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between text-xs font-bold text-white mb-1">
                        <span className="text-emerald-400">DAY 02 · LOCAL EXPERIENCE</span>
                        <span className="text-[10px] text-stone-400 font-normal">08:30 AM</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-stone-300 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
                        <span>LOCAL</span>
                        <span className="text-emerald-400/60">●────────●</span>
                        <span className="text-emerald-300 font-bold">EXPERIENCE</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[10px] text-stone-400">
                      <span>TEMPORAL FLOW OPTIMIZATION</span>
                      <span className="text-emerald-400 font-bold">-{counterValue}% PEAK QUEUE REDUCTION</span>
                    </div>
                  </div>
                </>
              )}

              {/* SCENE 04: Direct Panchayat Host Booking */}
              {index === 3 && (
                <>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-bold">
                    <Leaf className="w-3.5 h-3.5" />
                    <span>DIRECT HOST CONNECTION</span>
                  </div>

                  <div>
                    <h4 className="text-2xl sm:text-3xl font-extrabold uppercase tracking-tight text-white">
                      DIRECT PANCHAYAT HOST BOOKING
                    </h4>
                    <p className="text-xs font-mono text-stone-300 uppercase tracking-wider mt-1">
                      Pineview Orchid Cottage · Hosted by Gurung Family
                    </p>
                  </div>

                  <div className="p-4 sm:p-5 rounded-2xl bg-black/75 backdrop-blur-xl border border-white/15 space-y-3 font-mono">
                    <div className="flex items-center justify-between text-[10px] font-bold text-center gap-1.5">
                      <div className="flex-1 py-1.5 px-2 rounded-lg bg-white/5 border border-white/10 text-stone-300">
                        TRAVELER
                      </div>
                      <span className="text-amber-400 font-black">→</span>
                      <div className="flex-1 py-1.5 px-2 rounded-lg bg-amber-500/20 border border-amber-400/40 text-amber-300">
                        DIRECT LINK
                      </div>
                      <span className="text-amber-400 font-black">→</span>
                      <div className="flex-1 py-1.5 px-2 rounded-lg bg-emerald-500/20 border border-emerald-400/40 text-emerald-300">
                        LOCAL HOST
                      </div>
                    </div>

                    <div className="pt-2 border-t border-white/10 flex items-center justify-between">
                      <div>
                        <span className="text-[9px] uppercase text-stone-400 block font-semibold tracking-wider">
                          DIRECT HOST SHARE
                        </span>
                        <span className="text-2xl sm:text-3xl font-black text-emerald-400 mt-0.5 block">
                          {counterValue}% DIRECT SHARE
                        </span>
                        <span className="text-[10px] text-stone-300">
                          Verified Panchayat ledger · Bypasses middlemen
                        </span>
                      </div>

                      <div className="text-right">
                        <span className="text-[9px] uppercase text-stone-400 block font-semibold tracking-wider">
                          VILLAGE FUND
                        </span>
                        <span className="text-xs font-bold text-amber-300 mt-1 block">
                          +120 GREEN COINS
                        </span>
                        <span className="text-[10px] text-stone-400">
                          Trail & Youth Guide Fund
                        </span>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* SCENE 05: Yatri Mitra Emergency Net */}
              {index === 4 && (
                <>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-bold">
                    <Shield className="w-3.5 h-3.5" />
                    <span>TRAVELER SAFETY NET</span>
                  </div>

                  <div>
                    <h4 className="text-2xl sm:text-3xl font-extrabold uppercase tracking-tight text-white">
                      YATRI MITRA EMERGENCY NET
                    </h4>
                    <p className="text-xs font-mono text-stone-300 uppercase tracking-wider mt-1">
                      Calm High-Altitude Safety Infrastructure
                    </p>
                  </div>

                  <div className="p-4 sm:p-5 rounded-2xl bg-black/75 backdrop-blur-xl border border-white/15 space-y-3 font-mono text-xs">
                    <div className="flex items-center justify-between pb-2 border-b border-white/10">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-500/40 animate-pulse" />
                        <span className="text-white font-bold tracking-wider">{counterValue}</span>
                        <span className="text-stone-300">· SOS READY</span>
                      </div>
                      <span className="text-[10px] text-emerald-400 font-semibold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                        DISPATCH ONLINE
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-stone-300">
                      <span className="text-stone-400">GPS LOCATION:</span>
                      <span className="text-white font-bold">27.0594° N, 88.2625° E</span>
                    </div>

                    <div className="flex items-center justify-between text-stone-300">
                      <span className="text-stone-400">TRUSTED CONTACT:</span>
                      <span className="text-amber-300 font-bold">SYNCED · 4 WARDENS WITHIN 1.4KM</span>
                    </div>
                  </div>
                </>
              )}

            </div>
          </motion.div>
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* EDITORIAL STORY COPY WITH MULTI-LAYER PARALLAX (RIGHT COLUMN ~42%) */}
        {/* ------------------------------------------------------------------ */}
        <motion.div
          style={{ y: textColY }}
          className="lg:col-span-5 order-1 lg:order-2 flex flex-col justify-center space-y-6 min-h-[480px] sm:min-h-[540px] lg:min-h-[600px]"
        >
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0.5, x: 10 }}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          >
            {/* Step Number & Parallax Floating Highlight Badge Beside Text */}
            <div className="flex items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-3">
                <motion.span
                  style={{ y: stepNumY }}
                  className="text-4xl sm:text-5xl lg:text-6xl font-mono font-black text-amber-400 drop-shadow-[0_2px_12px_rgba(245,158,11,0.25)] select-none"
                >
                  {chapter.step}
                </motion.span>
                <span className="text-[11px] font-mono tracking-widest uppercase text-stone-300 font-bold bg-white/5 px-3 py-1.5 rounded-lg border border-white/10 backdrop-blur-sm">
                  {chapter.technicalLabel}
                </span>
              </div>

              {/* Floating Parallax Pill beside text (Chapters 1, 2, 3, 4, 5) */}
              <motion.div
                style={{ y: textBadgeY }}
                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/15 border border-amber-400/40 text-amber-300 text-[10px] font-mono font-bold uppercase tracking-wider shadow-md backdrop-blur-md"
              >
                <span>{chapter.textParallaxBadge.icon}</span>
                <span className="truncate max-w-[175px]">{chapter.textParallaxBadge.val}</span>
              </motion.div>
            </div>

            {/* Mobile Parallax Pill */}
            <div className="sm:hidden mb-3">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-400/40 text-amber-300 text-[10px] font-mono font-bold uppercase tracking-wider">
                <span>{chapter.textParallaxBadge.icon}</span>
                <span>{chapter.textParallaxBadge.val}</span>
              </div>
            </div>

            {/* Chapter Heading with Parallax Depth */}
            <motion.h3
              style={{ y: headingY }}
              className="text-2xl sm:text-3xl lg:text-4xl font-extrabold uppercase tracking-tight text-white leading-tight"
            >
              {chapter.chapterTitle}
            </motion.h3>

            {/* Story Lead Sentence */}
            <p className="text-lg sm:text-xl text-amber-200/90 font-serif italic mt-3 leading-snug">
              {chapter.storyHeading}
            </p>

            {/* Story Body Copy */}
            <div className="mt-4 space-y-3 text-sm sm:text-base text-stone-300 font-normal leading-relaxed">
              <p>{chapter.storyLead}</p>
              <p className="text-xs sm:text-sm text-stone-400 font-light">{chapter.storyDetail}</p>
            </div>

            {/* Parallax Accent Telemetry Card Beside Text */}
            <motion.div
              style={{ y: textAccentY }}
              className="mt-5 p-3.5 sm:p-4 rounded-xl bg-gradient-to-r from-stone-900/90 via-stone-950/80 to-stone-900/60 border border-white/10 border-l-2 border-l-amber-400/80 backdrop-blur-md shadow-lg"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-stone-400">
                  {chapter.accentMetric.label}
                </span>
                <span className="text-xs font-mono font-black text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                  {chapter.accentMetric.stat}
                </span>
              </div>
              <p className="text-[11px] sm:text-xs text-stone-300 font-mono mt-1 leading-snug">
                {chapter.accentMetric.sub}
              </p>
            </motion.div>

            {/* Action Link & Direct Launch Button */}
            <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between gap-4">
              <Link
                href={chapter.actionUrl}
                className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-stone-950 font-black text-xs font-mono uppercase tracking-wider transition-all duration-300 shadow-md hover:shadow-amber-400/20 active:scale-95 group"
              >
                <span>{chapter.actionText}</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-1" />
              </Link>

              <span className="text-[10px] font-mono text-stone-500 uppercase tracking-widest hidden sm:inline">
                CHAPTER {chapter.step} OF 05
              </span>
            </div>
          </motion.div>
        </motion.div>

      </div>
    </div>
  );
}

// ============================================================================
// MAIN HOW YATRI SETU WORKS COMPONENT
// ============================================================================

export function HowYatriSetuWorks() {
  const [activeChapter, setActiveChapter] = useState<number>(0);
  const containerRef = useRef<HTMLElement>(null);
  const isInView = useInView(containerRef, { once: true, amount: 0.1 });

  // Preload all visual assets
  useEffect(() => {
    FEATURE_CHAPTERS.forEach((ch) => {
      if (typeof window !== 'undefined') {
        const img = new window.Image();
        img.src = ch.image;
      }
    });
  }, []);

  const scrollToChapter = (id: string, idx: number) => {
    setActiveChapter(idx);
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <section
      ref={containerRef}
      className="relative w-full bg-[#0A0D12] text-white py-12 sm:py-16 overflow-hidden border-t border-stone-800/80"
      aria-label="How Yatri Setu Works — The Journey"
    >
      {/* Background ambient lighting and subtle texture */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,rgba(245,158,11,0.06),transparent)] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(#ffffff_0.5px,transparent_0.5px)] opacity-[0.025] pointer-events-none" />

      <div className="max-w-[1440px] mx-auto px-4 sm:px-8 lg:px-12 relative z-10">
        
        {/* ==================================================================== */}
        {/* SECTION HEADER (Large, Editorial, Premium)                           */}
        {/* ==================================================================== */}
        <div className="max-w-4xl mb-8 sm:mb-10">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center gap-2 mb-3"
          >
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span className="text-xs font-mono font-bold tracking-widest uppercase text-amber-400">
              THE YATRI SETU JOURNEY
            </span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.06] text-white uppercase"
          >
            FROM DESTINATION PRESSURE
            <br />
            <span className="font-serif italic font-normal text-amber-200/90 lowercase text-3xl sm:text-5xl lg:text-6xl">
              to a better journey.
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 15 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="text-base sm:text-lg text-stone-300 mt-4 leading-relaxed font-normal max-w-2xl text-balance"
          >
            Yatri Setu connects destination intelligence, smarter alternatives, local hosts and traveler safety into one continuous travel journey.
          </motion.p>
        </div>

        {/* ==================================================================== */}
        {/* STICKY FEATURE NAVIGATION BAR (5 Chapters)                           */}
        {/* ==================================================================== */}
        <div className="sticky top-16 sm:top-[72px] z-30 mb-6 py-3 bg-[#0A0D12]/85 backdrop-blur-2xl border-y border-stone-800/80 -mx-4 px-4 sm:-mx-8 sm:px-8 lg:-mx-12 lg:px-12">
          <div className="flex items-center gap-2 sm:gap-3 overflow-x-auto scrollbar-none no-scrollbar">
            {FEATURE_CHAPTERS.map((f, idx) => {
              const isActive = activeChapter === idx;

              return (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => scrollToChapter(f.id, idx)}
                  className={cn(
                    'shrink-0 px-4 py-2.5 rounded-xl border text-left transition-all duration-300 ease-out flex items-center gap-3 select-none cursor-pointer',
                    isActive
                      ? 'bg-amber-500/15 border-amber-400 text-white shadow-lg shadow-amber-500/10 ring-1 ring-amber-400/40'
                      : 'bg-stone-900/60 border-stone-800/80 hover:bg-stone-900 hover:border-stone-700 text-stone-400'
                  )}
                >
                  <span className={cn('text-sm font-black font-mono', isActive ? 'text-amber-400' : 'text-stone-500')}>
                    {f.step}
                  </span>
                  <span className="text-xs font-bold tracking-tight whitespace-nowrap">
                    {f.navTitle}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ==================================================================== */}
        {/* 5 CHAPTER ROWS (EACH CHAPTER HAS ITS OWN VISUAL BESIDE ITS TEXT)     */}
        {/* ==================================================================== */}
        <div className="space-y-4">
          {FEATURE_CHAPTERS.map((chapter, idx) => (
            <ChapterRow
              key={chapter.id}
              chapter={chapter}
              index={idx}
              onVisible={setActiveChapter}
            />
          ))}
        </div>

        {/* ==================================================================== */}
        {/* FUTURE-READY CINEMATIC CLOSING CTA                                   */}
        {/* ==================================================================== */}
        <div className="mt-20 sm:mt-28 pt-8">
          <div className="relative rounded-3xl overflow-hidden border border-white/10 bg-stone-900/80 p-8 sm:p-14 lg:p-20 text-center shadow-2xl">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <img
                src="/hero-himalaya.jpg"
                alt="End of journey Himalayan landscape"
                className="w-full h-full object-cover filter brightness-[0.35] scale-105"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/70 to-stone-950/40" />
            </div>

            <div className="relative z-10 max-w-3xl mx-auto space-y-6">
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

              <h3 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight uppercase">
                READY TO TRAVEL DIFFERENTLY?
              </h3>

              <p className="text-sm sm:text-base text-stone-300 max-w-xl mx-auto leading-relaxed">
                Choose a destination, understand the pressure, and discover a journey that fits you.
              </p>

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
