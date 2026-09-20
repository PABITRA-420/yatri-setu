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
import { DataSourcesPanel } from '@/components/DataSourcesPanel';
import { LiveFlowIntelligence } from '@/components/LiveFlowIntelligence';
import { SignatureFlowStory } from '@/components/SignatureFlowStory';
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

export default function HomePage() {
  const router = useRouter();
  const [popupTickerModalOpen, setPopupTickerModalOpen] = useState(false);
  const [activeTickerFilter, setActiveTickerFilter] = useState<'all' | 'calm' | 'critical'>('all');
  const [activeStep, setActiveStep] = useState(0);

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

  const regionalTickerData = [
    { id: 'darjeeling', name: 'Darjeeling', score: 88, level: 'CRITICAL', trend: '+14% vs avg', color: 'border-rose-500/40 bg-rose-500/10 text-rose-700 dark:text-rose-400', dot: 'bg-rose-500 animate-ping' },
    { id: 'kalimpong', name: 'Kalimpong', score: 42, level: 'MODERATE', trend: 'Balanced flow', color: 'border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' },
    { id: 'lava', name: 'Lava', score: 24, level: 'CALM', trend: 'Open trails', color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
    { id: 'lolegaon', name: 'Lolegaon', score: 18, level: 'SERENE', trend: 'Canopy open', color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
    { id: 'rishop', name: 'Rishop', score: 15, level: 'SERENE', trend: 'Crystal clear', color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
    { id: 'mirik', name: 'Mirik', score: 38, level: 'MODERATE', trend: 'Lake relaxed', color: 'border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' }
  ];

  const filteredTicker = useMemo(() => {
    if (activeTickerFilter === 'calm') {
      return regionalTickerData.filter(d => d.score < 30);
    }
    if (activeTickerFilter === 'critical') {
      return regionalTickerData.filter(d => d.score >= 50);
    }
    return regionalTickerData;
  }, [activeTickerFilter]);

  const categories = [
    {
      name: 'Mountains & Ridges',
      desc: 'High-altitude panoramic viewpoints away from commercial chokepoints',
      icon: Mountain,
      query: 'mountains',
      image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80',
      tag: 'Kanchenjunga Vista'
    },
    {
      name: 'Pine Woodlands & Nature',
      desc: 'Canopy walks and serene bird sanctuaries in undisturbed valleys',
      icon: Trees,
      query: 'nature',
      image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=600&q=80',
      tag: 'Neora Valley'
    },
    {
      name: 'Heritage & Monasteries',
      desc: 'Ancient gompas and silent sacred traditions with local monks',
      icon: Landmark,
      query: 'monasteries',
      image: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80',
      tag: 'Historic Gompas'
    },
    {
      name: 'Alpine Trails & Treks',
      desc: 'Pristine rhododendron hiking paths with certified village guides',
      icon: Footprints,
      query: 'trails',
      image: 'https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=600&q=80',
      tag: 'Certified Guides'
    },
    {
      name: 'Panchayat Homestays',
      desc: 'Panchayat-registered cottages where 90% of tariff directly supports hosts',
      icon: HomeIcon,
      query: 'homestays',
      image: 'https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=600&q=80',
      tag: '90% Host Payout'
    },
    {
      name: 'Flora & Photography',
      desc: 'Exotic orchid nurseries and cloud sea sunrise horizons',
      icon: Camera,
      query: 'orchids',
      image: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=600&q=80',
      tag: 'Orchid Ridge'
    }
  ];

  const demoSteps = [
    {
      step: '01',
      title: 'Real-Time Bottleneck Detection',
      badge: 'Score: 88/100 Alert',
      summary: 'Tourist queries Darjeeling; deterministic 6-factor engine flags critical gridlock on Hill Cart Road.',
      actionUrl: '/destinations/darjeeling/crowd',
      actionText: 'Inspect Darjeeling Diagnostics'
    },
    {
      step: '02',
      title: 'AI Similarity & Capacity Match',
      badge: '87% Similarity',
      summary: 'Alternative engine suggests Kalimpong & Rishop: 42% cost savings, 15/100 crowd score, zero queue time.',
      actionUrl: '/destinations/darjeeling/alternatives',
      actionText: 'View Alternative Advisor'
    },
    {
      step: '03',
      title: 'Adaptive Crowd-Smart Itinerary',
      badge: 'Day-by-Day Flow',
      summary: 'Dynamic route generator spaces activities to avoid peak hours and channels visits to local artisans.',
      actionUrl: '/itinerary',
      actionText: 'Try Itinerary Planner'
    },
    {
      step: '04',
      title: 'Direct Panchayat Host Booking',
      badge: '90% Direct Host Share',
      summary: 'Reserve verified village cottages with transparent ledger payments and Green Credit eco-discounts.',
      actionUrl: '/homestays',
      actionText: 'Browse Panchayat Stays'
    },
    {
      step: '05',
      title: 'Yatri Mitra Emergency Net (SOS)',
      badge: 'National 112 & GPS',
      summary: 'One-tap emergency broadcast links tourist coordinates with local village volunteers and safety desks.',
      actionUrl: '/safety/sos',
      actionText: 'Launch Safety SOS Terminal'
    }
  ];

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

      {/* 6. IMMERSIVE HIMALAYAN THEMES (Category Tiles) */}
      <section className="relative w-full py-16 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10 pb-4 border-b border-stone-200 dark:border-stone-800">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-widest text-amber-700 dark:text-amber-400 font-mono">
                Curated Escapes
              </span>
              <h2 className="text-3xl sm:text-5xl font-extrabold text-stone-950 dark:text-white tracking-tight mt-1">
                Immersive Himalayan Themes
              </h2>
            </div>
            <p className="text-sm text-stone-500 dark:text-stone-400 max-w-md leading-relaxed">
              Explore destinations categorized by their natural rhythm, altitude serenity, and cultural heritage.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((cat) => {
              const Icon = cat.icon;
              return (
                <Link
                  key={cat.name}
                  href={`/destinations?query=${encodeURIComponent(cat.query)}`}
                  className="group relative h-80 rounded-3xl overflow-hidden border border-stone-200 dark:border-stone-800 shadow-md hover:shadow-2xl transition-all duration-500 flex flex-col justify-end p-7"
                >
                  <img
                    src={cat.image}
                    alt={cat.name}
                    className="absolute inset-0 w-full h-full object-cover group-hover:scale-108 transition-transform duration-700 ease-out filter brightness-[0.82]"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-stone-950/95 via-stone-950/50 to-transparent" />

                  <div className="relative z-10 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center text-amber-300 border border-white/20">
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="px-2.5 py-1 rounded-full bg-black/40 backdrop-blur-md border border-white/20 text-[10px] font-mono text-amber-300 font-bold uppercase">
                        {cat.tag}
                      </span>
                    </div>

                    <h3 className="font-extrabold text-xl text-white group-hover:text-amber-300 transition-colors flex items-center justify-between">
                      <span>{cat.name}</span>
                      <ArrowUpRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-all transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                    </h3>

                    <p className="text-xs text-stone-300 line-clamp-2 leading-relaxed">
                      {cat.desc}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* 7. FEATURED CURATED SANCTUARIES */}
      <section className="relative w-full py-16 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10 pb-4 border-b border-stone-200 dark:border-stone-800">
            <div>
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-amber-700 dark:text-amber-400" />
                <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-950 dark:text-white tracking-tight">
                  Featured Himalayan Sanctuaries
                </h2>
              </div>
              <p className="text-sm text-stone-500 dark:text-stone-400 mt-1">
                Compare crowd footprints and choose regenerative travel
              </p>
            </div>

            <Button
              asChild
              variant="outline"
              className="rounded-2xl text-xs font-bold border-stone-300 dark:border-stone-700"
            >
              <Link href="/destinations" className="flex items-center gap-1.5">
                <span>View All 12 Circuit Sanctuaries</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {sampleDestinations.map((d) => (
              <DestinationCard key={d.id} destination={d} />
            ))}
          </div>
        </div>
      </section>

      {/* 8. INTERACTIVE 5-STEP DEMO WALKTHROUGH */}
      <section className="relative w-full py-16 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-stone-950 text-white rounded-[2.5rem] p-8 sm:p-14 shadow-2xl border border-stone-800 relative overflow-hidden">
            <div className="max-w-3xl mb-10 relative z-10">
              <span className="text-xs uppercase font-extrabold text-amber-400 tracking-widest font-mono">
                Smart Flow Execution Demo
              </span>
              <h2 className="text-3xl sm:text-5xl font-extrabold mt-2 tracking-tight">
                End-to-End Traveler Decongestion Journey
              </h2>
              <p className="text-sm text-stone-300 mt-3 leading-relaxed">
                Click through the 5-step lifecycle showing how Yatri Setu safeguards fragile mountain ecosystems while giving travelers an unforgettable experience:
              </p>
            </div>

            {/* Stepper Tabs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 relative z-10 mb-8">
              {demoSteps.map((s, idx) => (
                <button
                  key={s.step}
                  type="button"
                  onClick={() => setActiveStep(idx)}
                  className={cn(
                    'p-4 rounded-2xl border text-left transition-all flex flex-col justify-between',
                    activeStep === idx
                      ? 'bg-amber-500/15 border-amber-500/60 shadow-lg shadow-amber-500/10'
                      : 'bg-white/5 border-white/10 hover:bg-white/10 text-stone-300'
                  )}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className={cn(
                        'text-2xl font-black font-mono',
                        activeStep === idx ? 'text-amber-400' : 'text-stone-500'
                      )}>
                        {s.step}
                      </span>
                      <span className={cn(
                        'text-[10px] font-mono px-2 py-0.5 rounded-full font-bold',
                        activeStep === idx
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-white/5 text-stone-400'
                      )}>
                        {s.badge}
                      </span>
                    </div>
                    <h4 className={cn(
                      'font-bold text-xs sm:text-sm',
                      activeStep === idx ? 'text-white' : 'text-stone-300'
                    )}>
                      {s.title}
                    </h4>
                  </div>
                </button>
              ))}
            </div>

            {/* Active Step Details Card */}
            <div className="bg-stone-900/90 rounded-2xl p-6 sm:p-8 border border-stone-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
              <div className="space-y-2 max-w-2xl">
                <div className="flex items-center gap-2 text-xs font-mono text-amber-400 font-bold">
                  <span>PHASE {demoSteps[activeStep].step} ACTIVE</span>
                  <span>•</span>
                  <span>{demoSteps[activeStep].badge}</span>
                </div>
                <h3 className="text-xl sm:text-2xl font-extrabold text-white">
                  {demoSteps[activeStep].title}
                </h3>
                <p className="text-sm text-stone-300 leading-relaxed">
                  {demoSteps[activeStep].summary}
                </p>
              </div>

              <div className="shrink-0 flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
                <Button
                  asChild
                  className="w-full sm:w-auto bg-amber-400 hover:bg-amber-300 text-stone-950 font-extrabold text-xs h-11 px-6 rounded-xl shadow-lg"
                >
                  <Link href={demoSteps[activeStep].actionUrl} className="flex items-center justify-center gap-2">
                    <span>{demoSteps[activeStep].actionText}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </Button>
              </div>
            </div>

            {/* Direct Quick Launch Bar */}
            <div className="mt-8 pt-6 border-t border-white/10 flex flex-wrap items-center gap-4 relative z-10 text-xs">
              <Link
                href="/destinations/darjeeling/crowd"
                className="text-stone-300 hover:text-white flex items-center gap-1.5 font-medium"
              >
                <Flame className="w-3.5 h-3.5 text-amber-400" />
                <span>Darjeeling Crowd Simulator</span>
              </Link>
              <span className="text-stone-600">•</span>
              <Link
                href="/safety/sos"
                className="text-stone-300 hover:text-white flex items-center gap-1.5 font-medium"
              >
                <RadioTower size={14} className="text-rose-400" />
                <span>Emergency SOS Screen</span>
              </Link>
              <span className="text-stone-600">•</span>
              <Link
                href="/admin/command-center"
                className="text-stone-300 hover:text-white flex items-center gap-1.5 font-medium"
              >
                <Activity className="w-3.5 h-3.5 text-sky-400" />
                <span>Command Center Live Telemetry</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 9. BOTTOM CALL TO ACTION: Safety Assurance & Community Pledge */}
      <section className="relative w-full py-12 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-amber-500/10 via-emerald-500/10 to-amber-500/10 rounded-3xl p-8 sm:p-12 border border-amber-500/30 text-center space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 text-xs font-bold font-mono">
              <Leaf className="w-3.5 h-3.5" />
              <span>Smart India Hackathon 2026 Core Vision</span>
            </div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-stone-950 dark:text-white tracking-tight">
              Ready to experience tranquil Himalayan travel?
            </h2>
            <p className="text-sm text-stone-600 dark:text-stone-300 max-w-xl mx-auto leading-relaxed">
              Skip the tourist bottlenecks. Support local village homestay hosts and travel with complete peace of mind.
            </p>
            <div className="pt-2 flex flex-wrap items-center justify-center gap-4">
              <Button
                asChild
                className="bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs h-11 px-6 rounded-xl shadow-md"
              >
                <Link href="/destinations" className="flex items-center gap-2">
                  <Compass className="w-4 h-4" />
                  <span>Discover Village Sanctuaries</span>
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                className="border-stone-300 dark:border-stone-700 font-bold text-xs h-11 px-6 rounded-xl"
              >
                <Link href="/itinerary" className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>Generate Adaptive AI Itinerary</span>
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

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
