'use client';

import React, { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Search,
  Flame,
  Sparkles,
  ShieldCheck,
  MapPin,
  ArrowRight,
  Users,
  TrendingDown,
  Leaf,
  Compass,
  CheckCircle2,
  Calendar,
  Mountain,
  Trees,
  Landmark,
  Footprints,
  Camera,
  Home as HomeIcon,
  ArrowUpRight,
  Activity,
  AlertTriangle,
  HeartHandshake,
  Clock,
  Shield,
  Percent,
  Coins,
  ChevronRight,
  Navigation
} from 'lucide-react';
import { DestinationCard } from '@/components/DestinationCard';
import { DestinationIntelligence } from '@/components/DestinationIntelligence';
import { HowYatriSetuWorks } from '@/components/HowYatriSetuWorks';
import { DataSourcesPanel } from '@/components/DataSourcesPanel';
import { LiveFlowIntelligence } from '@/components/LiveFlowIntelligence';
import { SignatureFlowStory } from '@/components/SignatureFlowStory';
import HimalayanThemesGallery from '@/components/HimalayanThemesGallery';
import { Button } from '@/components/animate-ui/components/buttons/button';
import { RadioTower } from '@/components/animate-ui/icons/radio-tower';
import { X } from '@/components/animate-ui/icons/x';
import { AnimateIcon } from '@/components/animate-ui/icons/icon';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { DestinationSummary } from '@/types';
import { cn } from '@/lib/utils';
import { fetchDestinations } from '@/lib/api';

export default function HomePage() {
  const router = useRouter();
  const [popupTickerModalOpen, setPopupTickerModalOpen] = useState(false);
  const [activeTickerFilter, setActiveTickerFilter] = useState<'all' | 'calm' | 'critical'>('all');

  // Handle keyboard escape and body scroll locking for the modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setPopupTickerModalOpen(false);
      }
    };
    if (popupTickerModalOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [popupTickerModalOpen]);

  const sampleDestinations: DestinationSummary[] = [
    {
      id: 'darjeeling',
      name: 'Darjeeling',
      tagline: 'Colonial tea heritage & Himalayan railway facing heavy holiday congestion',
      region: 'Eastern Himalayas',
      state: 'West Bengal',
      hero_image: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
      crowd_score: 88,
      crowd_level: 'VERY HIGH',
      avg_cost_per_day_inr: 4800,
      tags: ['Heritage Rail', 'Tiger Hill', 'High Congestion']
    },
    {
      id: 'kalimpong',
      name: 'Kalimpong',
      tagline: 'Tranquil orchid ridge, vibrant monasteries & 87% similarity match',
      region: 'Eastern Himalayas',
      state: 'West Bengal',
      hero_image: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=800&q=80',
      crowd_score: 42,
      crowd_level: 'MEDIUM',
      avg_cost_per_day_inr: 2800,
      tags: ['Orchids', 'Serene Ridge', 'Recommended Alternative']
    },
    {
      id: 'rishop',
      name: 'Rishop',
      tagline: '360° panoramic Kanchenjunga sunrise haven without Tiger Hill queues',
      region: 'Eastern Himalayas',
      state: 'West Bengal',
      hero_image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80',
      crowd_score: 15,
      crowd_level: 'LOW',
      avg_cost_per_day_inr: 2200,
      tags: ['Sunrise Ridge', 'Dark Sky', 'Zero Traffic']
    },
    {
      id: 'lava',
      name: 'Lava',
      tagline: 'Misty pine woodlands & pristine gateway to Neora Valley National Park',
      region: 'Eastern Himalayas',
      state: 'West Bengal',
      hero_image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80',
      crowd_score: 24,
      crowd_level: 'LOW',
      avg_cost_per_day_inr: 2100,
      tags: ['Pine Forest', 'Birding', 'Misty Trails']
    }
  ];

  const [regionalTickerData, setRegionalTickerData] = useState([
    { id: 'darjeeling', name: 'Darjeeling', score: 88, level: 'CRITICAL', trend: '+14% vs avg', color: 'border-rose-500/40 bg-rose-500/10 text-rose-700 dark:text-rose-400', dot: 'bg-rose-500 animate-ping' },
    { id: 'kalimpong', name: 'Kalimpong', score: 42, level: 'MODERATE', trend: 'Balanced flow', color: 'border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' },
    { id: 'lava', name: 'Lava', score: 24, level: 'CALM', trend: 'Open trails', color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
    { id: 'lolegaon', name: 'Lolegaon', score: 18, level: 'SERENE', trend: 'Canopy open', color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
    { id: 'rishop', name: 'Rishop', score: 15, level: 'SERENE', trend: 'Crystal clear', color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
    { id: 'mirik', name: 'Mirik', score: 38, level: 'MODERATE', trend: 'Lake relaxed', color: 'border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' }
  ]);

  useEffect(() => {
    let isMounted = true;
    fetchDestinations()
      .then((items) => {
        if (isMounted && items && items.length > 0) {
          setRegionalTickerData((prev) =>
            prev.map((t) => {
              const live = items.find((x) => x.id === t.id);
              if (!live) return t;
              return {
                ...t,
                score: live.crowd_score,
                level: live.crowd_level.toUpperCase()
              };
            })
          );
        }
      })
      .catch((err) => {
        console.warn('Using offline fallback destinations on homepage:', err);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredTicker = useMemo(() => {
    if (activeTickerFilter === 'calm') {
      return regionalTickerData.filter(d => d.score < 30);
    }
    if (activeTickerFilter === 'critical') {
      return regionalTickerData.filter(d => d.score >= 50);
    }
    return regionalTickerData;
  }, [activeTickerFilter, regionalTickerData]);





  return (
    <div className="pb-28">
      {/* 1. HERO SECTION: Full Viewport Height/Width Immersive Himalayan Photography */}
      <section className="relative w-full min-h-screen flex flex-col justify-between pt-0 overflow-hidden bg-stone-950">
        <div className="relative min-h-screen w-full flex flex-col justify-between p-6 sm:p-12 lg:p-20 text-white overflow-hidden">
          {/* Full-bleed Background Immersive Photography */}
          <div className="absolute inset-0 z-0">
            <img
              src="/hero-himalaya.jpg"
              alt="Majestic Himalayan peaks overlooking sacred river valley at golden sunrise"
              className="w-full h-full object-cover object-center scale-105 transition-transform duration-1000 ease-out filter brightness-[0.88]"
            />
            {/* Cinematic Multi-stop Gradient Overlays for High Legibility */}
            <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/45 to-stone-950/25" />
            <div className="absolute inset-0 bg-gradient-to-r from-stone-950/90 via-stone-950/50 to-transparent" />
            {/* Seamless Bottom Blend Mask to Section 2 */}
            <div className="absolute inset-x-0 bottom-0 h-44 bg-gradient-to-b from-transparent via-stone-950/70 to-stone-950 pointer-events-none" />
          </div>

          {/* Hero Top Badges: Moved Higher Up to Top */}
          <div className="relative z-10 pt-2 sm:pt-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-emerald-500/40 text-emerald-300 text-xs font-bold tracking-wide font-mono shadow-md">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>Live Himalayan Telemetry Active</span>
              </div>

              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-amber-500/40 text-amber-300 text-xs font-semibold tracking-wide font-mono shadow-md">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>SIH 2026 Core Solution</span>
              </div>
            </div>
          </div>

          {/* Hero Main Content Box */}
          <div className="relative z-10 max-w-5xl lg:max-w-6xl space-y-6 my-auto py-8">
            {/* Headline with Brand Editorial Accent */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-extrabold tracking-tight leading-[1.04] text-white drop-shadow-md">
              <span className="block whitespace-nowrap text-3xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-[5rem] 2xl:text-8xl font-extrabold tracking-tight bg-gradient-to-r from-[#FF9933] via-white to-[#138808] bg-clip-text text-transparent pb-1">
                EXPLORE RURAL INDIA
              </span>
              Travel beyond <br />
              <span className="font-editorial italic font-normal text-amber-300 text-6xl sm:text-7xl lg:text-8xl xl:text-9xl">
                the congested ridges.
              </span>
            </h1>

            {/* Improved Tagline Text */}
            <p className="text-xl sm:text-2xl text-amber-100/90 font-editorial italic font-medium tracking-wide leading-relaxed drop-shadow-sm">
              "Explore the unseen, collect the moments."
            </p>

            {/* Explore & Contact Us Buttons */}
            <div className="flex flex-wrap items-center gap-3 md:flex-row pt-2">
              <Button variant="outline" asChild className="rounded-xl border-white/30 bg-stone-900/60 hover:bg-stone-900/90 text-white hover:text-amber-300 hover:border-amber-400/50 font-bold px-7 h-12 text-base sm:text-lg shadow-md backdrop-blur-md transition-all">
                <Link href="/destinations" className="text-white hover:text-amber-300">Explore</Link>
              </Button>
              <Button variant="outline" asChild className="rounded-xl border-white/30 bg-stone-900/60 hover:bg-stone-900/90 text-white hover:text-amber-300 hover:border-amber-400/50 font-bold px-7 h-12 text-base sm:text-lg shadow-md backdrop-blur-md transition-all">
                <Link href="/contact" className="text-white hover:text-amber-300">Contact Us</Link>
              </Button>
            </div>

            {/* Live Real-Time Decongestion Alert Banner */}
            <div className="inline-flex flex-col sm:flex-row items-start sm:items-center gap-3 p-3.5 pr-4 rounded-2xl bg-stone-900/80 backdrop-blur-xl border border-rose-500/30 text-xs shadow-xl">
              <div className="flex items-center gap-2 font-bold text-rose-300">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 animate-pulse" />
                <span>LIVE OVERCROWD ALERT:</span>
              </div>
              <span className="text-stone-300">
                Darjeeling Tiger Hill peak congestion <span className="font-mono font-bold text-rose-400">(88/100)</span>.
              </span>
              <Link
                href="/destinations/darjeeling/alternatives"
                className="inline-flex items-center gap-1 font-bold text-amber-400 hover:text-amber-300 underline underline-offset-4"
              >
                <span>Switch to Kalimpong (42/100, 87% match)</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 2. WHY YATRI-SETU SECTION: Full Screen / Max Height & Width with hero2.jpg */}
      <section className="relative w-full min-h-screen flex flex-col justify-start items-center pt-8 sm:pt-12 pb-16 px-4 sm:px-6 lg:px-8 text-white overflow-hidden bg-stone-950">
        {/* Full-bleed Background Immersive Photography hero2.jpg */}
        <div className="absolute inset-0 z-0">
          <img
            src="/hero2.jpg"
            alt="Scenic Himalayan range backdrop"
            className="w-full h-full object-cover object-center scale-105 transition-transform duration-1000 ease-out filter brightness-[0.7] contrast-105"
          />
          {/* Seamless Top Fade connecting Section 1 and Section 2 without visible line */}
          <div className="absolute inset-x-0 top-0 h-44 bg-gradient-to-b from-stone-950 via-stone-950/80 to-transparent pointer-events-none" />
          {/* Cinematic Multi-stop Dark Gradient Overlays for high legibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/70 to-transparent" />
          <div className="absolute inset-0 bg-black/45" />
          {/* Seamless Bottom Fade to Section 3 */}
          <div className="absolute inset-x-0 bottom-0 h-36 bg-gradient-to-t from-stone-950 to-transparent pointer-events-none" />
        </div>

        {/* Content Container */}
        <div className="relative z-10 max-w-6xl w-full mx-auto space-y-8">
          {/* Top Big Text: Why Yatri-setu? */}
          <div className="text-center space-y-3">
            <h2 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white drop-shadow-lg">
              Why <span className="font-editorial italic font-normal text-amber-300 text-5xl sm:text-7xl lg:text-8xl">Yatri-setu?</span>
            </h2>
            <p className="text-base sm:text-xl text-stone-200 max-w-3xl mx-auto leading-relaxed font-normal drop-shadow-sm">
              Conventional booking portals exacerbate gridlocks in fragile mountain hotspots. Yatri Setu actively balances tourist footfall, guarantees authentic homestay payouts, and provides 24/7 traveler safety.
            </p>
          </div>

          {/* Feature Accordion Container - Clean line style with desktop width and 1-4 numbering */}
          <div className="w-full pt-2">
            <Accordion multiple defaultValue={["engine"]}>
              {/* Accordion Item 1: Explainable Crowd Engine */}
              <AccordionItem value="engine">
                <AccordionTrigger>
                  <div className="flex items-center">
                    <span className="font-mono text-amber-400 font-black mr-3 sm:mr-5 text-xl sm:text-2xl lg:text-3xl">01</span>
                    <span>Explainable Crowd Engine &amp; Zero Hallucinations</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2 text-stone-200">
                    <p className="text-base sm:text-lg leading-relaxed text-stone-300">
                      Our deterministic 6-factor baseline recalculates real-time crowd telemetry across Darjeeling, Kalimpong, and the Eastern Himalayan circuit with zero artificial intelligence hallucinations.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">Multi-Factor Baseline</div>
                        <div className="text-sm text-stone-300">Continuous telemetry of footfall, booking density, seasonality, holidays, weather, and transit bottlenecks.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">Dynamic Road Pressure</div>
                        <div className="text-sm text-stone-300">Predictive congestion algorithms calculate entry wait times and alert drivers before highway gridlocks form.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">Algorithmic Integrity</div>
                        <div className="text-sm text-stone-300">Every score is mathematically grounded with explainable provenance and open telemetry metrics.</div>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Accordion Item 2: Suggested Alternatives */}
              <AccordionItem value="alternatives">
                <AccordionTrigger>
                  <div className="flex items-center">
                    <span className="font-mono text-emerald-400 font-black mr-3 sm:mr-5 text-xl sm:text-2xl lg:text-3xl">02</span>
                    <span>Capacity-Aware Alternative Advisor (42% Cost Savings)</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2 text-stone-200">
                    <p className="text-base sm:text-lg leading-relaxed text-stone-300">
                      When fragile hotspots like Darjeeling reach critical congestion (88/100), our suitability engine evaluates scenic geography, road access, and microclimates to recommend serene, uncrowded alternatives.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">Intelligent Match Scoring</div>
                        <div className="text-sm text-stone-300">Recommends Kalimpong (87% match, 42/100 crowd score) and Rishop (15/100) with identical Kanchenjunga vistas.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">Significant Traveler Savings</div>
                        <div className="text-sm text-stone-300">Save up to 42% on authentic heritage accommodations, village homestays, and local transportation.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">Zero Queue Entry</div>
                        <div className="text-sm text-stone-300">Bypass 3-hour dawn vehicle queues on Tiger Hill while enjoying serene, unobstructed Himalayan horizons.</div>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Accordion Item 3: Green Credits */}
              <AccordionItem value="green-credits">
                <AccordionTrigger>
                  <div className="flex items-center">
                    <span className="font-mono text-[#FF2A00] font-black mr-3 sm:mr-5 text-xl sm:text-2xl lg:text-3xl">03</span>
                    <span>Green Credits™ &amp; 90% Direct Host Tariff Distribution</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2 text-stone-200">
                    <p className="text-base sm:text-lg leading-relaxed text-stone-300">
                      Yatri Setu removes extractive booking intermediary commissions. By distributing 90% of tariff directly to panchayat-registered families, we empower local communities while rewarding eco-conscious travelers.{' '}
                      <Link
                        href="/dashboard"
                        className="underline underline-offset-4 text-emerald-400 hover:text-emerald-300 font-medium transition-colors cursor-pointer inline-flex items-center gap-1"
                      >
                        Click here
                      </Link>
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-teal-300 uppercase tracking-wider">In-Platform Green Tokens</div>
                        <div className="text-sm text-stone-300">Earn Green Credits™ automatically for choosing off-peak dates, low-pressure valleys, and eco-friendly stays.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-teal-300 uppercase tracking-wider">Direct Host Payouts</div>
                        <div className="text-sm text-stone-300">Transparent payment ledgers guarantee verified Himalayan hosts receive 90% of nightly charges directly.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-teal-300 uppercase tracking-wider">Redeemable Rewards</div>
                        <div className="text-sm text-stone-300">Convert earned tokens into direct discounts on future bookings, certified guide treks, and local organic produce.</div>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Accordion Item 4: Yatri Mitra Safety Net */}
              <AccordionItem value="safety">
                <AccordionTrigger>
                  <div className="flex items-center">
                    <span className="font-mono text-rose-400 font-black mr-3 sm:mr-5 text-xl sm:text-2xl lg:text-3xl">04</span>
                    <span>Yatri Mitra Safety Net &amp; 1-Tap Emergency SOS (112)</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2 text-stone-200">
                    <p className="text-base sm:text-lg leading-relaxed text-stone-300">
                      High-altitude mountain terrain demands dependable emergency response. Our one-tap safety broadcast connects travelers directly with regional community volunteer desks and national first responders.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-rose-400 uppercase tracking-wider">1-Tap GPS Broadcast</div>
                        <div className="text-sm text-stone-300">Broadcasts real-time latitude/longitude coordinates and medical tags directly to nearest registered volunteers.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-rose-400 uppercase tracking-wider">Direct National Link (112/1363)</div>
                        <div className="text-sm text-stone-300">Integrated direct-dial links with India's 112 Unified Emergency Service and 1363 24x7 Tourist Helpline.</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                        <div className="text-xs font-mono font-bold text-rose-400 uppercase tracking-wider">Offline Cache Mode</div>
                        <div className="text-sm text-stone-300">Critical contacts, nearest primary health centers, and certified village volunteers remain accessible offline.</div>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Accordion Item 5: Others */}
              <AccordionItem value="others">
                <AccordionTrigger>
                  <div className="flex items-center">
                    <span className="font-mono text-cyan-400 font-black mr-3 sm:mr-5 text-xl sm:text-2xl lg:text-3xl">05</span>
                    <span>Others</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2 text-stone-200 text-base sm:text-lg pl-10 sm:pl-16">
                    <ul className="space-y-3 font-normal">
                      <li className="flex items-start gap-3">
                        <span className="font-mono text-cyan-400 font-bold shrink-0">i.</span>
                        <span className="text-stone-300">Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod.</span>
                      </li>
                      <li className="flex items-start gap-3">
                        <span className="font-mono text-cyan-400 font-bold shrink-0">ii.</span>
                        <span className="text-stone-300">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi.</span>
                      </li>
                      <li className="flex items-start gap-3">
                        <span className="font-mono text-cyan-400 font-bold shrink-0">iii.</span>
                        <div className="relative inline-flex items-center group/tip">
                          <button
                            type="button"
                            onClick={() => setPopupTickerModalOpen(true)}
                            className="underline underline-offset-4 text-white hover:text-cyan-300 font-medium transition-colors cursor-pointer text-left"
                            aria-label="Click here to view live regional crowd ticker"
                          >
                            Click here
                          </button>
                          {/* Tooltip on hover */}
                          <div className="pointer-events-none absolute left-1/2 -translate-x-1/2 bottom-full mb-2.5 opacity-0 group-hover/tip:opacity-100 group-hover/tip:translate-y-0 translate-y-1 transition-all duration-200 ease-out z-30 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-stone-900 text-cyan-300 text-xs font-mono font-semibold whitespace-nowrap shadow-2xl border border-cyan-500/40 backdrop-blur-xl">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                            <span>Live Regional Crowd Ticker</span>
                            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-stone-900" />
                          </div>
                        </div>
                      </li>
                    </ul>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </section>



      {/* 3. LIVE FLOW INTELLIGENCE: Core Innovation */}
      <LiveFlowIntelligence onOpenCalculator={() => setPopupTickerModalOpen(true)} />



      {/* 4. SIGNATURE YATRI SETU FLOW STORY: Scroll-driven Visual Journey */}
      <SignatureFlowStory />

      {/* 6. IMMERSIVE HIMALAYAN THEMES (Find Your Himalayan Rhythm Gallery) */}
      <HimalayanThemesGallery />

      {/* 7. DESTINATION INTELLIGENCE (ESCAPE THE PRESSURE. FIND YOUR PLACE.) */}
      <DestinationIntelligence />

      {/* 8. HOW YATRI SETU WORKS: CINEMATIC SCROLL + PARALLAX + FEATURE JOURNEY */}
      <HowYatriSetuWorks />



      {/* Live Data Sources Panel — System Provenance & Live Providers */}
      <section className="relative w-full pb-16 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <DataSourcesPanel />
        </div>
      </section>

      {/* 2. REGIONAL CROWD DENSITY TICKER: Interactive 6-Factor Live Dashboard Modal */}
      {popupTickerModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-300 overflow-hidden"
          onClick={() => setPopupTickerModalOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="regional-ticker-modal-title"
        >
          {/* Full-Page Background hero1.jpg with gentle blur */}
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat filter blur-[3px] scale-105 pointer-events-none"
            style={{ backgroundImage: "url('/image2.png')" }}
          />
          {/* Subtle tinted scrim overlay */}
          <div className="absolute inset-0 bg-stone-950/70 backdrop-blur-[2px] pointer-events-none" />

          <div
            className="relative max-w-5xl w-full bg-[#0c1017]/95 border border-white/15 rounded-3xl p-5 sm:p-8 pt-6 sm:pt-8 shadow-[0_25px_80px_rgba(0,0,0,0.9)] space-y-6 animate-in zoom-in-95 duration-200 max-h-[92vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Top-Right Bold Animated Cross Close Button */}
            <button
              type="button"
              onClick={() => setPopupTickerModalOpen(false)}
              aria-label="Close modal"
              className="absolute top-4 right-4 sm:top-6 sm:right-6 p-2 sm:p-2.5 rounded-xl bg-white/10 hover:bg-rose-500/20 text-stone-200 hover:text-rose-400 border border-white/15 hover:border-rose-500/40 transition-all cursor-pointer flex items-center justify-center group shadow-md z-30"
            >
              <AnimateIcon animateOnHover>
                <X size={20} strokeWidth={2.8} className="text-stone-200 group-hover:text-rose-400 transition-colors" />
              </AnimateIcon>
            </button>

            {/* Header + Filters */}
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-5 border-b border-white/10">
              <div className="space-y-2">
                <h2
                  id="regional-ticker-modal-title"
                  className="font-extrabold text-xl sm:text-2xl text-white tracking-tight"
                >
                  Live Regional Crowd Density Ticker
                </h2>
                <div className="flex items-center gap-2.5 flex-wrap">
                  <span className="relative flex h-3 w-3 shrink-0">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                  </span>
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/15 border border-amber-500/35 text-amber-300 text-xs font-mono font-bold">
                    <RadioTower animate={true} loop={true} size={14} className="text-amber-400 shrink-0" />
                    <span>Deterministic Live Telemetry</span>
                  </div>
                  <p className="text-xs sm:text-sm text-stone-400">
                    Eastern Himalayan Circuit (North Bengal &amp; Sikkim Foothills) • Real-time Corridor Load
                  </p>
                </div>
              </div>

              {/* Filter Tabs with generous right margin to leave proper gap from the cross icon */}
              <div className="flex items-center gap-1 p-1 bg-white/5 border border-white/10 rounded-xl text-xs font-semibold shrink-0 mr-12 sm:mr-14">
                <button
                  type="button"
                  onClick={() => setActiveTickerFilter('all')}
                  className={cn(
                    'px-3 py-1.5 rounded-lg transition-all',
                    activeTickerFilter === 'all'
                      ? 'bg-white text-stone-950 font-extrabold shadow-sm'
                      : 'text-stone-400 hover:text-white'
                  )}
                >
                  All 6 Nodes
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTickerFilter('calm')}
                  className={cn(
                    'px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5',
                    activeTickerFilter === 'calm'
                      ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40'
                      : 'text-stone-400 hover:text-white'
                  )}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span>Serene (&lt;30)</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTickerFilter('critical')}
                  className={cn(
                    'px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5',
                    activeTickerFilter === 'critical'
                      ? 'bg-rose-500/20 text-rose-300 font-bold border border-rose-500/40'
                      : 'text-stone-400 hover:text-white'
                  )}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                  <span>Choked (&gt;50)</span>
                </button>
              </div>
            </div>

            {/* Grid of Nodes */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
              {filteredTicker.map((d) => (
                <Link
                  key={d.id}
                  href={`/destinations/${d.id}/crowd`}
                  onClick={() => setPopupTickerModalOpen(false)}
                  className={cn(
                    'group p-4 rounded-2xl border transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl flex flex-col justify-between text-center bg-stone-900/60 hover:bg-stone-800/80',
                    d.color
                  )}
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] font-mono uppercase tracking-wider font-bold">
                        {d.level}
                      </span>
                      <span className={cn('w-2 h-2 rounded-full', d.dot)} />
                    </div>
                    <span className="text-sm font-extrabold text-white block group-hover:text-amber-400 transition-colors">
                      {d.name}
                    </span>
                  </div>

                  <div className="my-3">
                    <div className="text-3xl font-black font-mono tracking-tight text-white">
                      {d.score}
                      <span className="text-xs font-normal text-stone-400">/100</span>
                    </div>
                    <div className="w-full bg-white/10 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className={cn(
                          'h-full rounded-full transition-all duration-500',
                          d.score > 70 ? 'bg-rose-500' : d.score > 35 ? 'bg-amber-500' : 'bg-emerald-500'
                        )}
                        style={{ width: `${d.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="text-[11px] text-stone-300 font-medium">
                    {d.trend}
                  </div>
                </Link>
              ))}
            </div>

            {/* 6-Factor Live Dashboard Sub-Metrics */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-stone-400 uppercase tracking-wider block">Real-time Telemetry Stream</span>
                <span className="text-sm font-bold text-emerald-400 font-mono flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block"></span>
                  Active (1.2s Sync)
                </span>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-stone-400 uppercase tracking-wider block">Factor Calibration</span>
                <span className="text-sm font-bold text-cyan-300 font-mono">6/6 Deterministic</span>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-stone-400 uppercase tracking-wider block">NH-10 Transit Load</span>
                <span className="text-sm font-bold text-amber-300 font-mono">Stable / Moderate</span>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-stone-400 uppercase tracking-wider block">Homestay Capacity</span>
                <span className="text-sm font-bold text-purple-300 font-mono">Panchayat Verified</span>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs text-stone-400">
              <span className="flex items-center gap-1.5 font-mono text-[11px]">
                <Activity className="w-3.5 h-3.5 text-amber-400" />
                <span>Deterministic 6-Factor Baseline + Live Telemetry Active</span>
              </span>
              <Link
                href="/admin/command-center"
                onClick={() => setPopupTickerModalOpen(false)}
                className="font-bold text-amber-400 hover:text-amber-300 hover:underline flex items-center gap-1 transition-colors"
              >
                <span>View Full Telemetry Command Center</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
