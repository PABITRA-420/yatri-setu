'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Homestay } from '@/types';
import { fetchHomestays } from '@/lib/api';
import { HomestayCard } from '@/components/HomestayCard';
import { 
  Home, 
  ShieldCheck, 
  HeartHandshake, 
  Sparkles, 
  MapPin, 
  Filter 
} from 'lucide-react';

function HomestaysContent() {
  const searchParams = useSearchParams();
  const initialDest = searchParams.get('destination_id') || 'kalimpong';

  const [destinationFilter, setDestinationFilter] = useState(initialDest);
  const [homestays, setHomestays] = useState<Homestay[]>([]);
  const [loading, setLoading] = useState(true);

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
    { id: 'kalimpong', label: 'Kalimpong (Recommended)' },
    { id: 'lava', label: 'Lava (Pine Edge)' },
    { id: 'rishop', label: 'Rishop (Kanchenjunga Facing)' }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 font-bold text-xs uppercase tracking-wider mb-2">
          <HeartHandshake className="w-3.5 h-3.5" />
          <span>Regenerative Rural Livelihoods</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
          Verified Rural & Panchayat Homestays
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 max-w-2xl mt-1">
          Every homestay is locally verified with village panchayats. Stay with Himalayan families, experience organic cooking, and contribute directly to community development.
        </p>
      </div>

      {/* Community Impact Callout */}
      <div className="bg-gradient-to-r from-emerald-900 via-slate-900 to-emerald-950 text-white rounded-2xl p-5 sm:p-6 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-sm sm:text-base">
              Yatri Setu Rural Community Guarantee
            </h3>
            <p className="text-xs text-slate-300">
              Zero middlemen commission. 100% of the room tariff goes directly to host families, plus a 10% contribution to the village rural development fund.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto shrink-0 text-xs font-semibold bg-white/10 px-3 py-1.5 rounded-xl border border-white/10">
          <span>✓ 100% Verified Hosts</span>
          <span>•</span>
          <span>✓ Clean Water & Hygiene Certified</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
        <span className="text-slate-400 font-semibold flex items-center gap-1 shrink-0">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter by Town:</span>
        </span>

        {destOptions.map((opt) => (
          <button
            key={opt.id}
            onClick={() => setDestinationFilter(opt.id)}
            className={`px-3.5 py-2 rounded-xl font-bold whitespace-nowrap transition-all ${
              destinationFilter === opt.id
                ? 'bg-amber-600 text-white shadow-sm'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Homestay Listings Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-96 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          ))}
        </div>
      ) : homestays.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
          <p className="text-slate-500 text-sm">No homestays available for this destination.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {homestays.map((hs) => (
            <HomestayCard key={hs.id} homestay={hs} />
          ))}
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
