'use client';

import React, { useState } from 'react';
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
  ChevronRight,
  Shield,
  ArrowUpRight
} from 'lucide-react';
import { DestinationCard } from '@/components/DestinationCard';
import { DestinationSummary } from '@/types';

export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTravelers, setSelectedTravelers] = useState('2 Guests');
  const [travelPace, setTravelPace] = useState('Moderate');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim().toLowerCase() === 'darjeeling') {
      router.push('/destinations/darjeeling/crowd');
    } else if (searchQuery.trim()) {
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

  const categories = [
    {
      name: 'Mountains & Ridges',
      desc: 'High-altitude panoramic viewpoints away from commercial chokepoints',
      icon: Mountain,
      query: 'mountains',
      image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80'
    },
    {
      name: 'Pine Woodlands & Nature',
      desc: 'Canopy walks and serene bird sanctuaries in undisturbed valleys',
      icon: Trees,
      query: 'nature',
      image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=600&q=80'
    },
    {
      name: 'Heritage & Monasteries',
      desc: 'Ancient gompas and silent sacred traditions with local monks',
      icon: Landmark,
      query: 'monasteries',
      image: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80'
    },
    {
      name: 'Alpine Trails & Treks',
      desc: 'Pristine rhododendron hiking paths with certified village guides',
      icon: Footprints,
      query: 'trails',
      image: 'https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=600&q=80'
    },
    {
      name: 'Panchayat Homestays',
      desc: 'Verified rural cottages where 100% of tariff directly supports hosts',
      icon: HomeIcon,
      query: 'homestays',
      image: 'https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=600&q=80'
    },
    {
      name: 'Flora & Photography',
      desc: 'Exotic orchid nurseries and cloud sea sunrise horizons',
      icon: Camera,
      query: 'orchids',
      image: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=600&q=80'
    }
  ];
  return (
    <div className="space-y-24 pb-28">
      {/* Hero Section: Full Screen Desktop Immersion with User Himalaya Image */}
      <section className="relative w-full pt-0">
        <div className="relative min-h-[92vh] w-full flex flex-col justify-between p-6 sm:p-12 lg:p-20 text-white overflow-hidden bg-stone-950">
          {/* Full-bleed Background Immersive Photography */}
          <div className="absolute inset-0 z-0">
            <img
              src="/hero-himalaya.jpg"
              alt="Majestic Himalayan peaks overlooking sacred river valley at golden sunrise"
              className="w-full h-full object-cover object-center scale-100 transition-transform duration-1000 ease-out filter brightness-[0.92]"
            />
            {/* Cinematic Gradient Overlays for High Legibility & Luxury Aesthetics */}
            <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/40 to-stone-950/20" />
            <div className="absolute inset-0 bg-gradient-to-r from-stone-950/85 via-stone-950/45 to-transparent" />
          </div>

          {/* Editorial Headline & Mission */}
          <div className="relative z-10 max-w-3xl space-y-6 pt-10 sm:pt-14">
            <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-black/40 backdrop-blur-md border border-white/20 text-amber-300 text-xs font-bold tracking-widest uppercase font-mono shadow-sm">
              <Leaf className="w-3.5 h-3.5 text-amber-400" />
              <span>Sustainable Himalayan Tourism &amp; Flow Intelligence</span>
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-extrabold tracking-tight leading-[1.05] text-white drop-shadow-md">
              Travel beyond <br />
              <span className="font-editorial italic font-normal text-amber-300 text-6xl sm:text-7xl lg:text-8xl xl:text-9xl">
                the congested ridges.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-stone-200 max-w-xl leading-relaxed font-medium drop-shadow-sm">
              When fragile Himalayan hotspots face critical overcrowding, Yatri Setu intelligently guides you to tranquil rural sanctuaries, certified panchayat homestays, and round-the-clock traveler safety coverage.
            </p>
          </div>

            {/* Floating Glass & Neomorphic Search Console */}
            <div className="relative z-10 mt-12">
              <div className="glass-panel p-4 sm:p-5 rounded-3xl max-w-4xl text-stone-900 dark:text-white shadow-2xl">
                <form
                  onSubmit={handleSearchSubmit}
                  className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center"
                >
                  {/* Segment 1: Destination Search */}
                  <div className="md:col-span-5 flex items-center gap-3.5 px-5 py-3.5 bg-stone-50 dark:bg-stone-900/90 rounded-2xl border border-stone-200/90 dark:border-white/10 shadow-inner">
                    <Search className="w-4 h-4 text-amber-700 dark:text-amber-400 shrink-0" />
                    <div className="w-full">
                      <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block font-mono">
                        Where do you want to escape?
                      </span>
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search e.g. Darjeeling, Kalimpong, Orchids..."
                        className="w-full bg-transparent text-xs sm:text-sm font-semibold focus:outline-none text-stone-950 dark:text-white placeholder:text-stone-400 placeholder:font-normal"
                      />
                    </div>
                  </div>

                  {/* Segment 2: Travel Window / Season */}
                  <div className="md:col-span-3 flex items-center gap-3 px-5 py-3.5 bg-stone-50 dark:bg-stone-900/90 rounded-2xl border border-stone-200/90 dark:border-white/10 shadow-inner">
                    <Calendar className="w-4 h-4 text-stone-400 shrink-0" />
                    <div>
                      <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block font-mono">
                        Window
                      </span>
                      <span className="text-xs font-semibold text-stone-800 dark:text-stone-200">
                        Autumn / Spring &apos;26
                      </span>
                    </div>
                  </div>

                  {/* Segment 3: Travelers & Bordered Button */}
                  <div className="md:col-span-4 flex items-center gap-3">
                    <div className="flex-1 flex items-center gap-2.5 px-4 py-3.5 bg-stone-50 dark:bg-stone-900/90 rounded-2xl border border-stone-200/90 dark:border-white/10 shadow-inner">
                      <Users className="w-4 h-4 text-stone-400 shrink-0" />
                      <select
                        value={selectedTravelers}
                        onChange={(e) => setSelectedTravelers(e.target.value)}
                        className="bg-transparent text-xs font-semibold text-stone-800 dark:text-stone-200 focus:outline-none w-full"
                      >
                        <option value="1 Solo Traveler">1 Solo Traveler</option>
                        <option value="2 Guests">2 Guests (Couple)</option>
                        <option value="Small Family (3-4)">Small Family (3-4)</option>
                        <option value="Group (5+)">Group (5+)</option>
                      </select>
                    </div>

                    <button
                      type="submit"
                      className="btn-neo-primary px-6 py-4 rounded-2xl text-xs font-bold tracking-tight whitespace-nowrap flex items-center gap-2"
                    >
                      <Flame className="w-4 h-4 text-amber-300" />
                      <span>Explore</span>
                    </button>
                  </div>
                </form>

                {/* Quick Suggestion Chips */}
                <div className="flex flex-wrap items-center gap-2 px-3 pt-3.5 text-xs text-stone-500 dark:text-stone-400">
                  <span className="text-[11px] font-bold tracking-wide uppercase font-mono text-stone-400">Quick Demo:</span>
                  {['Darjeeling', 'Kalimpong', 'Lava', 'Rishop'].map((item) => (
                    <button
                      key={item}
                      type="button"
                      onClick={() => {
                        setSearchQuery(item);
                        if (item === 'Darjeeling') router.push('/destinations/darjeeling/crowd');
                        else router.push(`/destinations/${item.toLowerCase()}`);
                      }}
                      className="px-3 py-1 rounded-xl bg-white/70 dark:bg-stone-800/80 hover:bg-stone-200 dark:hover:bg-stone-700 text-stone-800 dark:text-stone-200 text-[11px] font-semibold border border-stone-300/60 dark:border-white/10 transition-all active:scale-95"
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

      {/* Live Regional Crowd Density Ticker: Neomorphic Cards */}
      <section className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="neo-card rounded-3xl p-8 sm:p-10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-8 pb-4 border-b border-stone-200/80 dark:border-white/10">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-rose-500 animate-pulse" />
              <h2 className="font-extrabold text-base sm:text-lg text-stone-950 dark:text-white tracking-tight">
                Live Regional Crowd Density Ticker (North Bengal & Sikkim Circuit)
              </h2>
            </div>
            <span className="text-xs font-mono font-bold text-stone-400 uppercase tracking-wider">
              Deterministic 6-Factor Engine Active
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 sm:gap-5">
            {[
              { id: 'darjeeling', name: 'Darjeeling', score: 88, level: 'CRITICAL', color: 'border-rose-300/80 dark:border-rose-900/60 bg-rose-50/60 dark:bg-rose-950/20 text-rose-700 dark:text-rose-400', dot: 'bg-rose-500' },
              { id: 'kalimpong', name: 'Kalimpong', score: 42, level: 'MODERATE', color: 'border-amber-300/80 dark:border-amber-900/60 bg-amber-50/60 dark:bg-amber-950/20 text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' },
              { id: 'lava', name: 'Lava', score: 24, level: 'CALM', color: 'border-emerald-300/80 dark:border-emerald-900/60 bg-emerald-50/60 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
              { id: 'lolegaon', name: 'Lolegaon', score: 18, level: 'SERENE', color: 'border-emerald-300/80 dark:border-emerald-900/60 bg-emerald-50/60 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
              { id: 'rishop', name: 'Rishop', score: 15, level: 'SERENE', color: 'border-emerald-300/80 dark:border-emerald-900/60 bg-emerald-50/60 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
              { id: 'mirik', name: 'Mirik', score: 38, level: 'MODERATE', color: 'border-amber-300/80 dark:border-amber-900/60 bg-amber-50/60 dark:bg-amber-950/20 text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' }
            ].map((d) => (
              <Link
                key={d.id}
                href={`/destinations/${d.id}/crowd`}
                className={`p-5 rounded-2xl border-1.5 flex flex-col items-center justify-center text-center transition-all duration-300 hover:-translate-y-1.5 hover:shadow-md ${d.color}`}
              >
                <span className="text-xs font-extrabold text-stone-900 dark:text-stone-200">{d.name}</span>
                <span className="text-3xl font-black font-mono my-1.5">{d.score}<span className="text-xs font-normal text-stone-400">/100</span></span>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className={`w-2 h-2 rounded-full ${d.dot}`} />
                  <span className="text-[10px] font-bold uppercase tracking-wider font-mono">{d.level}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Experience / Category Section (Editorial Tiles) */}
      <section className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10 pb-4 border-b border-stone-200/80 dark:border-white/10">
          <div>
            <span className="text-xs font-extrabold uppercase tracking-widest text-amber-700 dark:text-amber-400 font-mono">
              Curated Escapes
            </span>
            <h2 className="text-3xl sm:text-5xl font-extrabold text-stone-950 dark:text-white tracking-tight mt-1">
              Immersive Himalayan Themes
            </h2>
          </div>
          <p className="text-sm text-stone-500 max-w-md leading-relaxed">
            Discover destinations defined by their environmental rhythm and local cultural character.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {categories.map((cat) => {
            const Icon = cat.icon;
            return (
              <Link
                key={cat.name}
                href={`/destinations?query=${encodeURIComponent(cat.query)}`}
                className="group relative h-72 rounded-[2rem] overflow-hidden border-1.5 border-stone-200/80 dark:border-white/10 shadow-sm hover:shadow-xl transition-all duration-500 flex flex-col justify-end p-8"
              >
                <img
                  src={cat.image}
                  alt={cat.name}
                  className="absolute inset-0 w-full h-full object-cover group-hover:scale-108 transition-transform duration-700 ease-out filter brightness-[0.85]"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-stone-950/95 via-stone-950/40 to-transparent" />

                <div className="relative z-10 space-y-2">
                  <div className="w-10 h-10 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center text-amber-300 mb-2 border border-white/20 shadow-sm">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-extrabold text-xl text-white group-hover:text-amber-300 transition-colors flex items-center justify-between">
                    <span>{cat.name}</span>
                    <ArrowUpRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </h3>
                  <p className="text-xs text-stone-300 line-clamp-2 leading-relaxed">
                    {cat.desc}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Core Differentiator: Active Tourist Flow Management */}
      <section className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="neo-card rounded-[2.5rem] p-10 sm:p-16">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 text-amber-800 dark:text-amber-400 font-extrabold text-xs uppercase tracking-wider mb-4 font-mono">
              <Sparkles className="w-4 h-4" />
              <span>SIH 2026 Core Innovation</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-stone-950 dark:text-white">
              Active Tourist Flow Management <br />
              <span className="font-editorial italic font-normal text-amber-700 dark:text-amber-400 text-4xl sm:text-6xl">
                vs. Generic Booking Portals
              </span>
            </h2>
            <p className="text-sm sm:text-base text-stone-600 dark:text-stone-400 mt-4 leading-relaxed">
              Standard booking sites exacerbate overtourism by channeling travelers into already choked corridors. 
              Yatri Setu actively redistributes footfall to sustain fragile Himalayan ecology and empower rural homestays.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="neo-card rounded-3xl p-8 hover:border-amber-500/40">
              <div className="w-14 h-14 rounded-2xl bg-amber-500/10 text-amber-700 dark:text-amber-400 flex items-center justify-center mb-6 border border-amber-500/20">
                <Flame className="w-7 h-7" />
              </div>
              <h3 className="font-extrabold text-lg text-stone-950 dark:text-white mb-2.5">
                Explainable Crowd Scoring
              </h3>
              <p className="text-xs sm:text-sm text-stone-600 dark:text-stone-400 leading-relaxed">
                Deterministic 6-factor algorithm combining historical footfall (35%), accommodation density (25%), seasonality (15%), holidays (10%), weather visibility (10%), and road choke points (5%).
              </p>
            </div>

            {/* Feature 2 */}
            <div className="neo-card rounded-3xl p-8 hover:border-emerald-500/40">
              <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 flex items-center justify-center mb-6 border border-emerald-500/20">
                <Sparkles className="w-7 h-7" />
              </div>
              <h3 className="font-extrabold text-lg text-stone-950 dark:text-white mb-2.5">
                Alternate-Destination Advisor
              </h3>
              <p className="text-xs sm:text-sm text-stone-600 dark:text-stone-400 leading-relaxed">
                When Darjeeling hits CRITICAL crowd levels (88/100), our similarity engine computes nearest quiet matches like Kalimpong (87% match, 42% cost savings) with natural language explanations.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="neo-card rounded-3xl p-8 hover:border-rose-500/40">
              <div className="w-14 h-14 rounded-2xl bg-rose-500/10 text-rose-700 dark:text-rose-400 flex items-center justify-center mb-6 border border-rose-500/20">
                <ShieldCheck className="w-7 h-7" />
              </div>
              <h3 className="font-extrabold text-lg text-stone-950 dark:text-white mb-2.5">
                Built-in Traveler Safety & SOS
              </h3>
              <p className="text-xs sm:text-sm text-stone-600 dark:text-stone-400 leading-relaxed">
                One-tap emergency broadcast with real-time GPS coordinates dispatched directly to local police, medical responders, and the verified Yatri Mitra rural volunteer network.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Curated Sanctuaries */}
      <section className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10 pb-4 border-b border-stone-200/80 dark:border-white/10">
          <div>
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-amber-700 dark:text-amber-400" />
              <h2 className="text-3xl sm:text-5xl font-extrabold text-stone-950 dark:text-white tracking-tight">
                Curated Himalayan Sanctuaries
              </h2>
            </div>
            <p className="text-sm text-stone-500 mt-1">
              Compare crowd footprints and choose regenerative travel
            </p>
          </div>

          <Link
            href="/destinations"
            className="btn-neo-secondary flex items-center gap-2 px-5 py-2.5 rounded-2xl text-xs font-bold"
          >
            <span>View all curated destinations</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {sampleDestinations.map((d) => (
            <DestinationCard key={d.id} destination={d} />
          ))}
        </div>
      </section>

      {/* Demo Flow Stepper Card */}
      <section className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="bg-stone-950 text-white rounded-[2.5rem] p-10 sm:p-16 shadow-2xl border border-stone-800 relative overflow-hidden">
          <div className="max-w-3xl mb-12 relative z-10">
            <span className="text-xs uppercase font-extrabold text-amber-400 tracking-widest font-mono">
              Interactive Platform Experience
            </span>
            <h2 className="text-4xl sm:text-5xl font-extrabold mt-2 tracking-tight">
              Tourist Decongestion Walkthrough
            </h2>
            <p className="text-sm text-stone-300 mt-3 leading-relaxed">
              Explore our intelligent 5-step workflow demonstrating end-to-end sustainable travel:
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5 relative z-10">
            {[
              { step: '01', title: 'Search Darjeeling', desc: 'Experience 88/100 CRITICAL crowd alert & bottleneck explanation' },
              { step: '02', title: 'Advisor Recommendation', desc: 'Kalimpong suggested with 87% similarity & 42% cost savings' },
              { step: '03', title: 'Generate Itinerary', desc: 'AI 3-day crowd-avoiding route and local cultural experiences' },
              { step: '04', title: 'Reserve Homestay', desc: 'Book verified Sherpa cottage with 10% community fund contribution' },
              { step: '05', title: 'Trigger Safety SOS', desc: 'Broadcast live GPS coords to police & Yatri Mitra volunteer responders' }
            ].map((s) => (
              <div key={s.step} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col justify-between hover:bg-white/10 transition-colors">
                <div>
                  <span className="text-3xl font-black text-amber-400 font-mono block mb-2">{s.step}</span>
                  <h4 className="font-extrabold text-sm text-white">{s.title}</h4>
                  <p className="text-xs text-stone-300 mt-2 leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 flex flex-wrap items-center gap-4 relative z-10">
            <Link
              href="/destinations/darjeeling/crowd"
              className="px-7 py-4 rounded-2xl bg-amber-400 hover:bg-amber-300 text-stone-950 font-extrabold text-xs shadow-lg active:scale-97 transition-all flex items-center gap-2 border border-amber-300"
            >
              <span>Begin Demo at Darjeeling Crowd Panel</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/safety/sos"
              className="px-6 py-4 rounded-2xl bg-white/10 hover:bg-white/15 text-white font-bold text-xs transition-colors border border-white/15"
            >
              Test Emergency SOS Screen
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
