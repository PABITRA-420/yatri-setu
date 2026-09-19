'use client';

import React, { useState, useMemo } from 'react';
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
import { Button } from '@/components/animate-ui/components/buttons/button';
import { RadioTower } from '@/components/animate-ui/icons/radio-tower';
import { DestinationSummary } from '@/types';
import { cn } from '@/lib/utils';

export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [travelPace, setTravelPace] = useState<'Relaxed' | 'Balanced' | 'High Adventure'>('Balanced');
  const [activeTickerFilter, setActiveTickerFilter] = useState<'all' | 'calm' | 'critical'>('all');
  const [activeStep, setActiveStep] = useState(0);
  const [travelDate, setTravelDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split('T')[0];
  });

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim().toLowerCase();
    if (query === 'darjeeling') {
      router.push('/destinations/darjeeling/crowd');
    } else if (query === 'kalimpong') {
      router.push('/destinations/kalimpong');
    } else if (query) {
      router.push(`/destinations?query=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      router.push('/destinations');
    }
  };

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
      {/* 1. HERO SECTION: Immersive Himalayan Photography + Live Decongestion Console */}
      <section className="relative w-full pt-0">
        <div className="relative min-h-[92vh] w-full flex flex-col justify-between p-6 sm:p-12 lg:p-20 text-white overflow-hidden bg-stone-950">
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
          </div>

          {/* Hero Content Box */}
          <div className="relative z-10 max-w-4xl space-y-6 pt-8 sm:pt-12">
            {/* Live Operational Status Chips */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/50 backdrop-blur-md border border-emerald-500/40 text-emerald-300 text-xs font-bold tracking-wide font-mono shadow-sm">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>Live Himalayan Telemetry Active</span>
              </div>

              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/50 backdrop-blur-md border border-amber-500/40 text-amber-300 text-xs font-semibold tracking-wide font-mono">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>SIH 2026 Core Solution</span>
              </div>
            </div>

            {/* Headline with Brand Editorial Accent */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-extrabold tracking-tight leading-[1.04] text-white drop-shadow-md">
              Travel beyond <br />
              <span className="font-editorial italic font-normal text-amber-300 text-6xl sm:text-7xl lg:text-8xl xl:text-9xl">
                the congested ridges.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-stone-200 max-w-2xl leading-relaxed font-normal drop-shadow-sm">
              When fragile Himalayan hotspots face critical overcrowding, <strong className="text-white font-bold">Yatri Setu</strong> actively balances tourist flow—guiding you to serene village alternatives, certified panchayat homestays, and round-the-clock traveler safety coverage.
            </p>

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

          {/* Interactive Floating Glass Search Console */}
          <div className="relative z-10 mt-10">
            <div className="bg-stone-900/80 dark:bg-stone-950/80 backdrop-blur-2xl p-4 sm:p-5 rounded-3xl max-w-4xl text-white shadow-2xl border border-white/15">
              <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
                {/* Segment 1: Destination Search */}
                <div className="md:col-span-5 relative flex items-center gap-3 px-4 py-3 bg-white/10 dark:bg-stone-900/90 rounded-2xl border border-white/10 shadow-inner group focus-within:border-amber-400 focus-within:ring-2 focus-within:ring-amber-500/20 transition-all">
                  <Search className="w-4 h-4 text-amber-400 shrink-0 self-center pointer-events-none" />
                  <div className="relative w-full">
                    <input
                      type="text"
                      id="hero_search_input"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search Darjeeling, Kalimpong, Lava..."
                      className="block w-full bg-transparent text-sm font-semibold focus:outline-none text-white placeholder:text-stone-400 placeholder:font-normal"
                    />
                  </div>
                </div>

                {/* Segment 2: Interactive Date Picker */}
                <div className="md:col-span-4 relative flex items-center gap-3 px-4 py-3 bg-white/10 dark:bg-stone-900/90 rounded-2xl border border-white/10 shadow-inner group focus-within:border-amber-400 focus-within:ring-2 focus-within:ring-amber-500/20 transition-all">
                  <Calendar className="w-4 h-4 text-amber-400 shrink-0 self-center pointer-events-none" />
                  <div className="relative w-full flex items-center justify-between">
                    <input
                      type="date"
                      id="hero_date_input"
                      value={travelDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={(e) => setTravelDate(e.target.value)}
                      className="block w-full bg-transparent text-sm font-semibold focus:outline-none text-white [color-scheme:dark] cursor-pointer"
                    />
                  </div>
                </div>

                {/* Segment 3: Explore Action Button */}
                <div className="md:col-span-3 flex items-center h-full">
                  <Button
                    type="submit"
                    className="w-full h-12 bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 hover:from-amber-600 hover:to-amber-800 text-stone-950 font-extrabold text-sm tracking-wide rounded-2xl shadow-lg shadow-amber-500/25 flex items-center justify-center gap-2 border border-amber-400/40 transition-all"
                  >
                    <Flame className="w-4 h-4 text-stone-950 fill-stone-950" />
                    <span>Explore Sanctuaries</span>
                  </Button>
                </div>
              </form>

              {/* Quick Search Chips & Filter Pills */}
              <div className="mt-3.5 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-stone-400 font-medium">Trending:</span>
                  {[
                    { label: 'Tiger Hill Alternative', query: 'kalimpong' },
                    { label: 'Neora Valley Pine', query: 'lava' },
                    { label: '360° Sunrise Ridge', query: 'rishop' }
                  ].map(chip => (
                    <button
                      key={chip.label}
                      type="button"
                      onClick={() => {
                        setSearchQuery(chip.query);
                        router.push(`/destinations/${chip.query}`);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/15 border border-white/10 text-stone-300 hover:text-white transition-colors text-[11px]"
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-1.5 text-stone-400 font-mono text-[11px]">
                  <span>Pace:</span>
                  {(['Relaxed', 'Balanced', 'High Adventure'] as const).map(p => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setTravelPace(p)}
                      className={cn(
                        'px-2 py-0.5 rounded-md transition-all',
                        travelPace === p
                          ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40'
                          : 'hover:text-stone-200'
                      )}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Impact Metric Proof Counter Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mt-6">
              <div className="bg-stone-900/60 backdrop-blur-md rounded-2xl p-3 border border-white/10">
                <span className="text-2xl font-black text-amber-400 font-mono">88 → 42</span>
                <p className="text-[11px] text-stone-300 font-medium mt-0.5">Average corridor crowd reduction</p>
              </div>
              <div className="bg-stone-900/60 backdrop-blur-md rounded-2xl p-3 border border-white/10">
                <span className="text-2xl font-black text-emerald-400 font-mono">90%</span>
                <p className="text-[11px] text-stone-300 font-medium mt-0.5">Direct tariff to rural homestay hosts</p>
              </div>
              <div className="bg-stone-900/60 backdrop-blur-md rounded-2xl p-3 border border-white/10">
                <span className="text-2xl font-black text-sky-400 font-mono">100%</span>
                <p className="text-[11px] text-stone-300 font-medium mt-0.5">Panchayat verified listings</p>
              </div>
              <div className="bg-stone-900/60 backdrop-blur-md rounded-2xl p-3 border border-white/10">
                <span className="text-2xl font-black text-rose-400 font-mono">24/7</span>
                <p className="text-[11px] text-stone-300 font-medium mt-0.5">Yatri Mitra & 112 emergency coverage</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. REGIONAL CROWD DENSITY TICKER: Interactive 6-Factor Live Dashboard */}
      <section className="relative w-full py-16 -mt-10 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white/90 dark:bg-[#121824]/90 backdrop-blur-2xl rounded-3xl p-6 sm:p-8 shadow-2xl border border-stone-200 dark:border-stone-800">
            {/* Header + Filters */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-stone-200 dark:border-stone-800">
              <div className="flex items-center gap-3">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                </span>
                <div>
                  <h2 className="font-extrabold text-lg sm:text-xl text-stone-950 dark:text-white tracking-tight">
                    Live Regional Crowd Density Ticker
                  </h2>
                  <p className="text-xs text-stone-500 dark:text-stone-400">
                    Eastern Himalayan Circuit (North Bengal &amp; Sikkim Foothills)
                  </p>
                </div>
              </div>

              {/* Filter Tabs */}
              <div className="flex items-center gap-1.5 p-1 bg-stone-100 dark:bg-stone-900 rounded-xl text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setActiveTickerFilter('all')}
                  className={cn(
                    'px-3 py-1.5 rounded-lg transition-all',
                    activeTickerFilter === 'all'
                      ? 'bg-white dark:bg-stone-800 text-stone-950 dark:text-white shadow-xs font-bold'
                      : 'text-stone-500 hover:text-stone-800 dark:hover:text-stone-200'
                  )}
                >
                  All 6 Nodes
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTickerFilter('calm')}
                  className={cn(
                    'px-3 py-1.5 rounded-lg transition-all flex items-center gap-1',
                    activeTickerFilter === 'calm'
                      ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-500/30'
                      : 'text-stone-500 hover:text-stone-800 dark:hover:text-stone-200'
                  )}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  <span>Serene (&lt;30)</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTickerFilter('critical')}
                  className={cn(
                    'px-3 py-1.5 rounded-lg transition-all flex items-center gap-1',
                    activeTickerFilter === 'critical'
                      ? 'bg-rose-500/15 text-rose-700 dark:text-rose-300 font-bold border border-rose-500/30'
                      : 'text-stone-500 hover:text-stone-800 dark:hover:text-stone-200'
                  )}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
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
                  className={cn(
                    'group p-4 rounded-2xl border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg flex flex-col justify-between text-center',
                    d.color
                  )}
                >
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-mono uppercase tracking-wider font-bold">
                        {d.level}
                      </span>
                      <span className={cn('w-2 h-2 rounded-full', d.dot)} />
                    </div>
                    <span className="text-sm font-extrabold text-stone-950 dark:text-white block group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">
                      {d.name}
                    </span>
                  </div>

                  <div className="my-3">
                    <div className="text-3xl font-black font-mono tracking-tight">
                      {d.score}
                      <span className="text-xs font-normal text-stone-500 dark:text-stone-400">/100</span>
                    </div>
                    <div className="w-full bg-stone-200 dark:bg-stone-800 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className={cn(
                          'h-full rounded-full',
                          d.score > 70 ? 'bg-rose-500' : d.score > 35 ? 'bg-amber-500' : 'bg-emerald-500'
                        )}
                        style={{ width: `${d.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="text-[10px] text-stone-500 dark:text-stone-400 font-medium">
                    {d.trend}
                  </div>
                </Link>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-stone-200/80 dark:border-stone-800/80 flex flex-wrap items-center justify-between text-xs text-stone-500 dark:text-stone-400">
              <span className="flex items-center gap-1.5 font-mono text-[11px]">
                <Activity className="w-3.5 h-3.5 text-amber-500" />
                <span>Deterministic 6-Factor Baseline + Live Telemetry Active</span>
              </span>
              <Link
                href="/admin/command-center"
                className="font-bold text-amber-700 dark:text-amber-400 hover:underline flex items-center gap-1"
              >
                <span>View Full Telemetry Command Center</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 3. LIVE DATA SOURCES PANEL: Provenance Transparency */}
      <section className="relative w-full py-4 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <DataSourcesPanel />
        </div>
      </section>

      {/* 4. CORE DIFFERENTIATOR: Active Tourist Flow Management vs Generic Booking Portals */}
      <section className="relative w-full py-16 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-stone-900 text-white rounded-[2.5rem] p-8 sm:p-14 shadow-2xl border border-stone-800 relative overflow-hidden">
            <div className="text-center max-w-3xl mx-auto mb-12">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/15 text-amber-300 font-mono text-xs font-bold uppercase tracking-wider mb-4 border border-amber-500/30">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Regenerative Tourism Infrastructure</span>
              </div>
              <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight">
                Active Tourist Flow Management <br />
                <span className="font-editorial italic font-normal text-amber-300 text-4xl sm:text-6xl">
                  vs. Conventional Booking Portals
                </span>
              </h2>
              <p className="text-sm sm:text-base text-stone-300 mt-4 leading-relaxed font-normal">
                Standard travel portals maximize commercial bookings into already choked corridors—worsening traffic jams, water crises, and surging prices. Yatri Setu actively redistributes footfall to sustain pristine Himalayan ecosystems.
              </p>
            </div>

            {/* 4 Feature Pillars */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Feature 1 */}
              <div className="bg-stone-800/80 rounded-3xl p-6 border border-stone-700/80 hover:border-amber-500/50 transition-all flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 rounded-2xl bg-amber-500/15 text-amber-400 flex items-center justify-center mb-5 border border-amber-500/30">
                    <Flame className="w-6 h-6" />
                  </div>
                  <h3 className="font-extrabold text-base text-white mb-2">
                    Explainable Crowd Engine
                  </h3>
                  <p className="text-xs text-stone-300 leading-relaxed">
                    Deterministic 6-factor baseline (footfall, booking density, seasonality, holidays, weather, transit chokepoints) coupled with dynamic road pressure recalculation.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-stone-700/60 text-[11px] font-mono text-amber-400 font-semibold">
                  Zero Hallucinations
                </div>
              </div>

              {/* Feature 2 */}
              <div className="bg-stone-800/80 rounded-3xl p-6 border border-stone-700/80 hover:border-emerald-500/50 transition-all flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 rounded-2xl bg-emerald-500/15 text-emerald-400 flex items-center justify-center mb-5 border border-emerald-500/30">
                    <Compass className="w-6 h-6" />
                  </div>
                  <h3 className="font-extrabold text-base text-white mb-2">
                    Suggested Alternatives
                  </h3>
                  <p className="text-xs text-stone-300 leading-relaxed">
                    When Darjeeling hits critical (88/100), our capacity-aware suitability engine evaluates road access and weather to suggest serene matches like Kalimpong (87% match).
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-stone-700/60 text-[11px] font-mono text-emerald-400 font-semibold">
                  42% Cost Savings
                </div>
              </div>

              {/* Feature 3: Green Credits */}
              <div className="bg-stone-800/80 rounded-3xl p-6 border border-emerald-500/40 bg-gradient-to-b from-emerald-500/10 to-transparent flex flex-col justify-between relative overflow-hidden">
                <div className="absolute top-3 right-3 px-2 py-0.5 rounded-full bg-emerald-500/20 text-[10px] font-mono font-bold text-emerald-300 border border-emerald-500/30">
                  Reward Loop
                </div>
                <div>
                  <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-5 border border-emerald-500/40">
                    <Leaf className="w-6 h-6" />
                  </div>
                  <h3 className="font-extrabold text-base text-white mb-2 flex items-center gap-1.5">
                    <span>Green Credits™</span>
                    <span>🌿</span>
                  </h3>
                  <p className="text-xs text-stone-300 leading-relaxed">
                    Earn in-platform tokens for picking low-pressure sanctuaries, off-peak travel dates, and village homestays. Redeemable directly for booking discounts.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-stone-700/60 flex items-center justify-between text-xs">
                  <span className="text-emerald-400 font-mono font-bold">30 pts discount ready</span>
                  <Link href="/dashboard" className="text-white hover:text-emerald-400 inline-flex items-center gap-1 font-semibold">
                    <span>Wallet</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>

              {/* Feature 4: Traveler Safety & SOS */}
              <div className="bg-stone-800/80 rounded-3xl p-6 border border-stone-700/80 hover:border-rose-500/50 transition-all flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 rounded-2xl bg-rose-500/15 text-rose-400 flex items-center justify-center mb-5 border border-rose-500/30">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <h3 className="font-extrabold text-base text-white mb-2">
                    Yatri Mitra Safety Net
                  </h3>
                  <p className="text-xs text-stone-300 leading-relaxed">
                    One-tap emergency broadcast transmitting GPS coordinates to regional Yatri Mitra community volunteers, alongside direct-dial national emergency helplines (112, 1363).
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-stone-700/60 text-[11px] font-mono text-rose-400 font-semibold">
                  1-Tap GPS Dispatch
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. SIDE-BY-SIDE VISUAL COMPARISON: Hotspot vs Alternative */}
      <section className="relative w-full py-16 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-widest text-amber-700 dark:text-amber-400 font-mono">
                Live Decongestion In Action
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-950 dark:text-white tracking-tight mt-1">
                Why Diverting Makes Pure Travel Sense
              </h2>
            </div>
            <p className="text-sm text-stone-500 dark:text-stone-400 max-w-md">
              Compare Darjeeling with its certified alternative Kalimpong to see how footfall balancing saves budget and stress.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Choked Hotspot Card */}
            <div className="p-8 rounded-3xl bg-rose-500/5 border-2 border-rose-500/30 dark:border-rose-500/20 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <span className="px-3 py-1 rounded-full bg-rose-500/15 text-rose-700 dark:text-rose-400 text-xs font-bold font-mono uppercase">
                  Traditional Choked Hotspot
                </span>
                <span className="text-xs font-bold text-rose-600 dark:text-rose-400 flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Critical Density</span>
                </span>
              </div>

              <h3 className="text-2xl font-extrabold text-stone-950 dark:text-white">
                Darjeeling Hill Station
              </h3>
              <p className="text-xs text-stone-600 dark:text-stone-300 mt-1">
                Facing severe gridlock along Ghoom-Tiger Hill and water scarcity.
              </p>

              <div className="grid grid-cols-3 gap-3 my-6">
                <div className="p-3.5 rounded-xl bg-white/80 dark:bg-stone-900/80 border border-stone-200 dark:border-stone-800 text-center">
                  <span className="text-2xl font-black font-mono text-rose-600">88/100</span>
                  <span className="text-[10px] text-stone-500 block uppercase font-bold mt-0.5">Crowd Pressure</span>
                </div>
                <div className="p-3.5 rounded-xl bg-white/80 dark:bg-stone-900/80 border border-stone-200 dark:border-stone-800 text-center">
                  <span className="text-2xl font-black font-mono text-stone-900 dark:text-white">₹4,800</span>
                  <span className="text-[10px] text-stone-500 block uppercase font-bold mt-0.5">Avg Tariff / Day</span>
                </div>
                <div className="p-3.5 rounded-xl bg-white/80 dark:bg-stone-900/80 border border-stone-200 dark:border-stone-800 text-center">
                  <span className="text-2xl font-black font-mono text-rose-600">2.5 hrs</span>
                  <span className="text-[10px] text-stone-500 block uppercase font-bold mt-0.5">Mall Rd Queue</span>
                </div>
              </div>

              <ul className="space-y-2 text-xs text-stone-600 dark:text-stone-300 mb-6">
                <li className="flex items-center gap-2 text-rose-700 dark:text-rose-400 font-medium">
                  <span>✕</span> Overpriced surge tariffs during peak sunrise hours
                </li>
                <li className="flex items-center gap-2 text-rose-700 dark:text-rose-400 font-medium">
                  <span>✕</span> Vehicle congestion causing severe carbon emission peaks
                </li>
                <li className="flex items-center gap-2 text-rose-700 dark:text-rose-400 font-medium">
                  <span>✕</span> Less than 25% tourist spend reaches local indigenous communities
                </li>
              </ul>

              <Button
                asChild
                variant="outline"
                className="w-full border-rose-500/30 text-rose-700 dark:text-rose-400 hover:bg-rose-500/10 rounded-xl font-bold text-xs"
              >
                <Link href="/destinations/darjeeling/crowd">
                  Inspect Darjeeling Diagnostic Data
                </Link>
              </Button>
            </div>

            {/* Smart Suggested Alternative Card */}
            <div className="p-8 rounded-3xl bg-emerald-500/5 border-2 border-emerald-500/40 dark:border-emerald-500/30 shadow-lg relative overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 text-xs font-bold font-mono uppercase border border-emerald-500/30">
                  Recommended Sanctuary Match
                </span>
                <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1 font-mono">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>87% Similarity Match</span>
                </span>
              </div>

              <h3 className="text-2xl font-extrabold text-stone-950 dark:text-white">
                Kalimpong Orchid Ridge
              </h3>
              <p className="text-xs text-stone-600 dark:text-stone-300 mt-1">
                Same panoramic Kanchenjunga views, serene colonial cottages, and zero queue delays.
              </p>

              <div className="grid grid-cols-3 gap-3 my-6">
                <div className="p-3.5 rounded-xl bg-white/80 dark:bg-stone-900/80 border border-stone-200 dark:border-stone-800 text-center">
                  <span className="text-2xl font-black font-mono text-emerald-600">42/100</span>
                  <span className="text-[10px] text-stone-500 block uppercase font-bold mt-0.5">Crowd Pressure</span>
                </div>
                <div className="p-3.5 rounded-xl bg-white/80 dark:bg-stone-900/80 border border-stone-200 dark:border-stone-800 text-center">
                  <span className="text-2xl font-black font-mono text-emerald-600">₹2,800</span>
                  <span className="text-[10px] text-stone-500 block uppercase font-bold mt-0.5">42% Savings</span>
                </div>
                <div className="p-3.5 rounded-xl bg-white/80 dark:bg-stone-900/80 border border-stone-200 dark:border-stone-800 text-center">
                  <span className="text-2xl font-black font-mono text-emerald-600">0 mins</span>
                  <span className="text-[10px] text-stone-500 block uppercase font-bold mt-0.5">Entry Wait</span>
                </div>
              </div>

              <ul className="space-y-2 text-xs text-stone-600 dark:text-stone-300 mb-6">
                <li className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-medium">
                  <span>✓</span> Direct 90% homestay host revenue distribution via Panchayat
                </li>
                <li className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-medium">
                  <span>✓</span> Quiet mountain trails and undisturbed pine canopy trails
                </li>
                <li className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-medium">
                  <span>✓</span> Earn +30 Green Credits™ toward next Himalayan trip
                </li>
              </ul>

              <Button
                asChild
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-md shadow-emerald-600/20"
              >
                <Link href="/destinations/darjeeling/alternatives">
                  <span>Select Kalimpong Alternative</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

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
    </div>
  );
}
