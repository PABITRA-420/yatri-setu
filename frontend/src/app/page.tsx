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
  Calendar
} from 'lucide-react';
import { DestinationCard } from '@/components/DestinationCard';
import { DestinationSummary } from '@/types';

export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

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
      tagline: 'Colonial tea hills & heritage toy train facing severe holiday congestion',
      region: 'Eastern Himalayas',
      state: 'West Bengal',
      hero_image: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
      crowd_score: 88,
      crowd_level: 'VERY HIGH',
      avg_cost_per_day_inr: 4800,
      tags: ['Toy Train', 'Tiger Hill', 'High Congestion']
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
      tags: ['Orchids', 'Serene', 'Deolo Hill', 'Recommended Alternative']
    },
    {
      id: 'rishop',
      name: 'Rishop',
      tagline: '360° panoramic Kanchenjunga sunrise haven without Tiger Hill crowds',
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

  return (
    <div className="space-y-16 pb-16">
      {/* SIH 2026 Interactive Demo Banner */}
      <div className="bg-gradient-to-r from-amber-600 via-rose-600 to-emerald-700 text-white py-2.5 px-4">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-2 font-medium">
            <span className="px-2 py-0.5 rounded bg-white/20 font-bold uppercase tracking-wider text-[10px]">
              SIH 2026 Core Flow
            </span>
            <span>
              Experience overtourism redirection: Search <strong>Darjeeling (88/100)</strong> → Recommends <strong>Kalimpong (87% Match)</strong>
            </span>
          </div>
          <Link
            href="/destinations/darjeeling/crowd"
            className="flex items-center gap-1 font-bold bg-white text-slate-900 px-3 py-1 rounded-lg hover:bg-slate-100 transition-colors shrink-0 text-[11px]"
          >
            <span>Launch Darjeeling Demo</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 pt-4">
        <div className="max-w-7xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden bg-slate-950 text-white min-h-[520px] flex items-center shadow-2xl">
            {/* Background Image & Overlay */}
            <div className="absolute inset-0 z-0">
              <img
                src="https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1800&q=85"
                alt="Himalayan Foothills"
                className="w-full h-full object-cover opacity-35 filter blur-[0.5px]"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/80 to-transparent" />
            </div>

            {/* Hero Text Content */}
            <div className="relative z-10 p-8 sm:p-14 max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-bold uppercase tracking-wider border border-amber-500/30 mb-5">
                <Leaf className="w-3.5 h-3.5" />
                <span>Hyperlocal & Rural Tourism With Traveler Safety</span>
              </div>

              <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] mb-4">
                Travel Beyond the Crowds. <br />
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-rose-300 to-emerald-400">
                  Discover Rural India.
                </span>
              </h1>

              <p className="text-sm sm:text-base text-slate-300 mb-8 leading-relaxed">
                Yatri Setu actively balances tourist footfall across vulnerable heritage corridors. 
                When famous mountain hotspots face critical overtourism, we intelligently guide you to serene rural alternatives, verified panchayat homestays, and round-the-clock emergency support.
              </p>

              {/* Smart Search Bar */}
              <form
                onSubmit={handleSearchSubmit}
                className="bg-white/95 backdrop-blur-md p-2 rounded-2xl shadow-xl flex flex-col sm:flex-row items-center gap-2 max-w-xl border border-white/20"
              >
                <div className="flex items-center gap-2.5 px-3 py-2 w-full text-slate-800">
                  <Search className="w-5 h-5 text-amber-600 shrink-0" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search e.g. 'Darjeeling', 'Kalimpong' or 'Orchids'..."
                    className="w-full bg-transparent text-sm focus:outline-none text-slate-900 placeholder:text-slate-400 font-medium"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white text-xs font-bold shadow-md shadow-amber-600/30 whitespace-nowrap active:scale-95 transition-all flex items-center justify-center gap-2"
                >
                  <Flame className="w-4 h-4 text-amber-300" />
                  <span>Check Crowd Index</span>
                </button>
              </form>

              {/* Popular quick tags */}
              <div className="flex flex-wrap items-center gap-2 mt-4 text-xs text-slate-400">
                <span className="font-semibold text-slate-300">Quick Demo Search:</span>
                {['Darjeeling', 'Kalimpong', 'Lava', 'Rishop'].map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => {
                      setSearchQuery(item);
                      if (item === 'Darjeeling') router.push('/destinations/darjeeling/crowd');
                      else router.push(`/destinations/${item.toLowerCase()}`);
                    }}
                    className="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-slate-200 text-xs transition-colors"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Live Crowd Heatmap Ticker */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
              <h2 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white uppercase tracking-wider">
                Live Regional Crowd Density Ticker (North Bengal Circuit)
              </h2>
            </div>
            <span className="text-xs text-slate-400">
              Deterministic 6-Factor Engine Active
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {[
              { id: 'darjeeling', name: 'Darjeeling', score: 88, level: 'VERY HIGH', color: 'bg-rose-500/10 text-rose-600 border-rose-500/20' },
              { id: 'kalimpong', name: 'Kalimpong', score: 42, level: 'MEDIUM', color: 'bg-amber-500/10 text-amber-600 border-amber-500/20' },
              { id: 'lava', name: 'Lava', score: 24, level: 'LOW', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' },
              { id: 'lolegaon', name: 'Lolegaon', score: 18, level: 'LOW', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' },
              { id: 'rishop', name: 'Rishop', score: 15, level: 'LOW', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' },
              { id: 'mirik', name: 'Mirik', score: 38, level: 'MEDIUM', color: 'bg-amber-500/10 text-amber-600 border-amber-500/20' }
            ].map((d) => (
              <Link
                key={d.id}
                href={`/destinations/${d.id}/crowd`}
                className={`p-3 rounded-xl border flex flex-col items-center justify-center text-center transition-all hover:scale-103 ${d.color}`}
              >
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{d.name}</span>
                <span className="text-lg font-black my-0.5">{d.score}<span className="text-[10px] font-normal">/100</span></span>
                <span className="text-[10px] font-bold uppercase tracking-wider">{d.level}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Core Differentiator: Active Tourist Flow Management */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-600 font-bold text-xs uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>SIH 2026 Core Differentiator</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-black tracking-tight text-slate-900 dark:text-white">
            Active Tourist Flow Management vs. Generic Booking Portals
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-2">
            Generic portals exacerbate overtourism by channeling travelers into already choked destinations. 
            Yatri Setu actively redistributes footfall to sustain local ecosystems and empower rural homestays.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:border-amber-500/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center mb-4">
              <Flame className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white mb-2">
              Explainable Crowd Scoring
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Deterministic 6-factor algorithm combining historical footfall (35%), accommodation density (25%), seasonality (15%), holidays (10%), weather visibility (10%), and traffic choke points (5%).
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:border-emerald-500/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white mb-2">
              Alternate-Destination Advisor
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              When Darjeeling hits VERY HIGH crowd levels (88/100), our similarity engine computes nearest quiet matches like Kalimpong (87% match, 42% cost savings) with natural language explanations.
            </p>
          </div>

          {/* Card 3 */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:border-rose-500/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-600 flex items-center justify-center mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white mb-2">
              Built-in Traveler Safety & SOS
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              One-tap emergency broadcast with real-time GPS coordinates dispatched directly to local police, medical responders, and the verified Yatri Mitra rural volunteer network.
            </p>
          </div>
        </div>
      </section>

      {/* Featured Destinations */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-amber-600" />
              <h2 className="text-xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
                Curated Himalayan Sanctuaries
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Compare crowd footprints and choose regenerative travel
            </p>
          </div>

          <Link
            href="/destinations"
            className="flex items-center gap-1 text-xs font-bold text-amber-600 hover:text-amber-700 transition-colors"
          >
            <span>View all 6 curated destinations</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {sampleDestinations.map((d) => (
            <DestinationCard key={d.id} destination={d} />
          ))}
        </div>
      </section>

      {/* Demo Flow Stepper Card */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950 text-white rounded-3xl p-8 sm:p-12 shadow-xl">
          <div className="max-w-3xl mb-8">
            <span className="text-xs uppercase font-bold text-amber-400 tracking-wider">
              Ready for Evaluation
            </span>
            <h2 className="text-2xl sm:text-4xl font-black mt-1">
              SIH 2026 Tourist Demo Walkthrough
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-2">
              Follow our official 10-step judging workflow demonstrating end-to-end decongestion:
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { step: '01', title: 'Search Darjeeling', desc: 'Experience 88/100 VERY HIGH crowd alert & bottleneck explanation' },
              { step: '02', title: 'Advisor Recommendation', desc: 'Kalimpong suggested with 87% similarity & 42% cost savings' },
              { step: '03', title: 'Generate Itinerary', desc: 'AI 3-day crowd-avoiding route and local cultural experiences' },
              { step: '04', title: 'Reserve Homestay', desc: 'Book verified Sherpa cottage with 10% community fund contribution' },
              { step: '05', title: 'Trigger Safety SOS', desc: 'Broadcast live GPS coords to police & Yatri Mitra volunteer responders' }
            ].map((s) => (
              <div key={s.step} className="bg-white/5 border border-white/10 rounded-2xl p-4 flex flex-col justify-between">
                <div>
                  <span className="text-2xl font-black text-amber-400 block mb-2">{s.step}</span>
                  <h4 className="font-bold text-sm text-white">{s.title}</h4>
                  <p className="text-xs text-slate-300 mt-1">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <Link
              href="/destinations/darjeeling/crowd"
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 text-white font-bold text-xs shadow-lg shadow-amber-500/20 active:scale-95 transition-all flex items-center gap-2"
            >
              <span>Begin Demo at Darjeeling Crowd Panel</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/safety/sos"
              className="px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs transition-colors"
            >
              Test Emergency SOS Screen
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
