'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Homestay } from '@/types';
import { fetchHomestays } from '@/lib/api';
import { HomestayCard } from '@/components/HomestayCard';
import { SkeletonCard, FetchProgressBar } from '@/components/SkeletonCard';
import { EmptyState } from '@/components/EmptyState';
import { Breadcrumbs } from '@/components/Breadcrumbs';
import { YatriMap } from '@/components/YatriMap';
import { formatINR } from '@/lib/utils';
import { 
  Home, 
  ShieldCheck, 
  HeartHandshake, 
  Sparkles, 
  MapPin, 
  Filter,
  Map,
  Grid,
  X,
  Star,
  CalendarCheck,
  CheckCircle2
} from 'lucide-react';
import { motion } from 'motion/react';
import Link from 'next/link';

function HomestaysContent() {
  const searchParams = useSearchParams();
  const rawParam = searchParams.get('destination') || searchParams.get('destination_id');
  const initialDest = rawParam ? rawParam.toLowerCase().trim() : 'all';

  const [destinationFilter, setDestinationFilter] = useState(initialDest);
  const [homestays, setHomestays] = useState<Homestay[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'map'>('grid');
  const [quickViewHomestay, setQuickViewHomestay] = useState<Homestay | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchHomestays(destinationFilter === 'all' ? undefined : destinationFilter);
      setHomestays(data);
      setLoading(false);
    }
    load();
  }, [destinationFilter]);

  const destOptions = [
    { id: 'all', label: 'All Himalayan Stays' },
    { id: 'darjeeling', label: 'Darjeeling' },
    { id: 'kalimpong', label: 'Kalimpong (Recommended)' },
    { id: 'lava', label: 'Lava (Pine Edge)' },
    { id: 'lolegaon', label: 'Lolegaon' },
    { id: 'rishop', label: 'Rishop (Kanchenjunga Facing)' },
    { id: 'mirik', label: 'Mirik' }
  ];

  return (
    <div className="max-w-[1440px] mx-auto px-4 sm:px-8 lg:px-12 py-8 space-y-8">
      <Breadcrumbs />

      {/* Header */}
      <div className="pb-6 border-b border-white/10 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-400/30 text-emerald-300 font-bold text-xs uppercase tracking-wider mb-2">
            <HeartHandshake className="w-3.5 h-3.5" />
            <span>Regenerative Rural Livelihoods • SIH 2026</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            Verified Rural & Panchayat Homestays
          </h1>
          <p className="text-xs sm:text-sm text-stone-400 max-w-2xl mt-2 leading-relaxed">
            Every homestay is locally verified with village gram panchayats. Stay with Himalayan host families, savor organic garden dining, and directly support village community development.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-2 p-1 bg-stone-900 border border-white/10 rounded-2xl self-start md:self-auto shrink-0">
          <button
            onClick={() => setViewMode('grid')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              viewMode === 'grid'
                ? 'bg-amber-400 text-stone-950 shadow-xs'
                : 'text-stone-400 hover:text-white'
            }`}
          >
            <Grid className="w-4 h-4" />
            <span>Grid View</span>
          </button>
          <button
            onClick={() => setViewMode('map')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              viewMode === 'map'
                ? 'bg-amber-400 text-stone-950 shadow-xs'
                : 'text-stone-400 hover:text-white'
            }`}
          >
            <Map className="w-4 h-4" />
            <span>Interactive Map</span>
          </button>
        </div>
      </div>

      {/* Community Impact Callout */}
      <div className="bg-stone-900/80 backdrop-blur-xl text-white rounded-[2.5rem] p-7 sm:p-9 shadow-xl border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-extrabold text-base sm:text-lg tracking-tight">
              Yatri Setu Rural Community Guarantee
            </h3>
            <p className="text-xs sm:text-sm text-stone-300 mt-0.5 leading-relaxed">
              Zero predatory commercial markups. 90% of booking value is policy-allocated to local host families, and 5% supports the Gram Panchayat village development fund.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start md:self-auto shrink-0 text-xs font-semibold bg-white/10 px-4 py-2 rounded-2xl border border-white/15">
          <span>✓ Panchayat Registered</span>
          <span>•</span>
          <span>✓ Hygiene Certified</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
        <span className="text-stone-400 font-bold uppercase tracking-wider text-[11px] flex items-center gap-1 shrink-0 mr-1">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter by Town:</span>
        </span>

        {destOptions.map((opt) => (
          <button
            key={opt.id}
            onClick={() => setDestinationFilter(opt.id)}
            className={`px-4 py-2 rounded-xl font-bold uppercase text-[11px] whitespace-nowrap transition-all active:scale-95 ${
              destinationFilter === opt.id
                ? 'bg-amber-400 text-stone-950 font-black shadow-xs'
                : 'bg-white/5 border border-white/10 text-stone-300 hover:bg-white/10'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <FetchProgressBar loading={loading} />

      {/* Map View Mode */}
      {viewMode === 'map' ? (
        <div className="h-[600px] rounded-3xl overflow-hidden border border-white/10 shadow-2xl relative">
          <YatriMap
            nodes={homestays.map((h) => ({
              id: h.id,
              name: h.title,
              coordinates: [88.4695, 27.0594],
              crowd_score: 25,
              crowd_level: 'LOW',
              capacity_status: 'HEALTHY',
              access_status: 'OPEN',
              tagline: h.tagline
            }))}
          />
        </div>
      ) : (
        /* Homestay Listings Grid */
        loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <SkeletonCard key={i} index={i} />
            ))}
          </div>
        ) : homestays.length === 0 ? (
          <EmptyState
            message="No verified homestays are currently available in this destination."
            onReset={() => setDestinationFilter('all')}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {homestays.map((hs, index) => (
              <motion.div
                key={hs.id}
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: index * 0.06 }}
              >
                <HomestayCard
                  homestay={hs}
                  onQuickView={(item) => setQuickViewHomestay(item)}
                />
              </motion.div>
            ))}
          </div>
        )
      )}

      {/* Quick View Drawer Modal */}
      {quickViewHomestay && (
        <div className="fixed inset-0 z-50 bg-stone-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-stone-900 border border-white/15 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-6 relative animate-in zoom-in-95 duration-200">
            <button
              onClick={() => setQuickViewHomestay(null)}
              className="absolute top-5 right-5 p-2 rounded-full bg-white/10 text-stone-300 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-4">
              <img
                src={quickViewHomestay.host.avatar_url}
                alt={quickViewHomestay.host.name}
                className="w-16 h-16 rounded-full object-cover border-2 border-amber-400"
              />
              <div>
                <span className="text-xs uppercase font-bold text-amber-400 tracking-wider">
                  Host Profile & Village Verification
                </span>
                <h2 className="text-xl font-extrabold text-white">{quickViewHomestay.host.name}</h2>
                <p className="text-xs text-stone-400">
                  Speaks {quickViewHomestay.host.languages.join(', ')} • Gram Panchayat Verified Host
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 bg-stone-950/60 p-4 rounded-2xl border border-white/5 text-xs">
              <div>
                <span className="text-stone-500 block">Homestay</span>
                <span className="font-bold text-white">{quickViewHomestay.title}</span>
              </div>
              <div>
                <span className="text-stone-500 block">Nightly Tariff</span>
                <span className="font-bold text-amber-300">{formatINR(quickViewHomestay.price_per_night_inr)}</span>
              </div>
              <div>
                <span className="text-stone-500 block">Village Development Contribution</span>
                <span className="font-bold text-emerald-400">{quickViewHomestay.community_fund_contribution_percent}% Fund</span>
              </div>
              <div>
                <span className="text-stone-500 block">Guest Rating</span>
                <span className="font-bold text-amber-400 flex items-center gap-1">
                  <Star className="w-3.5 h-3.5 fill-amber-400" />
                  {quickViewHomestay.rating} / 5.0
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase text-stone-400">Host Bio & Heritage</h4>
              <p className="text-xs text-stone-300 leading-relaxed bg-stone-950/40 p-4 rounded-2xl border border-white/5">
                {quickViewHomestay.host.about}
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase text-stone-400">Included Special Activity</h4>
              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-2xl text-xs text-amber-200">
                ✨ {quickViewHomestay.special_activity}
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <button
                onClick={() => setQuickViewHomestay(null)}
                className="px-5 py-2.5 rounded-xl bg-stone-800 text-stone-300 text-xs font-bold hover:bg-stone-700"
              >
                Close Preview
              </button>
              <Link
                href={`/booking/confirmation?homestay_id=${quickViewHomestay.id}`}
                className="btn-neo-primary px-6 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2"
              >
                <CalendarCheck className="w-4 h-4" />
                <span>Book This Stay Now</span>
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function HomestaysPage() {
  return (
    <Suspense fallback={
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading homestays...
      </div>
    }>
      <HomestaysContent />
    </Suspense>
  );
}
