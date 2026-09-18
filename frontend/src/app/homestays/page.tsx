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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="pb-6 border-b border-black/[.08]/80 dark:border-white/10">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-[#183A32] dark:text-emerald-400 font-bold text-xs uppercase tracking-wider mb-2">
          <HeartHandshake className="w-3.5 h-3.5" />
          <span>Regenerative Rural Livelihoods • SIH 2026</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-[#171714] dark:text-white tracking-tight">
          Verified Rural & Panchayat Homestays
        </h1>
        <p className="text-xs sm:text-sm text-[#706E68] max-w-2xl mt-2 leading-relaxed">
          Every homestay is locally verified with village gram panchayats. Stay with Himalayan host families, savor organic garden dining, and directly support village community development.
        </p>
      </div>

      {/* Community Impact Callout */}
      <div className="bg-stone-950 text-white rounded-[2.5rem] p-7 sm:p-9 shadow-[0_12px_40px_rgba(23,23,20,0.06)] border border-stone-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-[20px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-extrabold text-base sm:text-lg tracking-tight">
              Yatri Setu Rural Community Guarantee
            </h3>
            <p className="text-xs sm:text-sm text-stone-300 mt-0.5 leading-relaxed">
              Zero middlemen commission. 100% of room tariff goes directly to host families, plus a 10% contribution to the village rural development fund.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start md:self-auto shrink-0 text-xs font-semibold bg-[#FCFAF6]/10 px-4 py-2 rounded-[20px] border border-white/10">
          <span>✓ 100% Verified Hosts</span>
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
            className={`px-4 py-2 rounded-xl font-bold uppercase text-[11px] whitespace-nowrap transition-all ${
              destinationFilter === opt.id
                ? 'bg-stone-950 dark:bg-[#FCFAF6] text-white dark:text-[#171714] shadow-xs'
                : 'bg-[#F5F2EA] dark:bg-stone-800 text-[#706E68] dark:text-stone-300 hover:bg-stone-200/70 dark:hover:bg-stone-700'
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
            <div key={i} className="h-96 bg-slate-200 dark:bg-slate-800 rounded-[20px]" />
          ))}
        </div>
      ) : homestays.length === 0 ? (
        <div className="text-center py-16 bg-[#FCFAF6] dark:bg-slate-900 rounded-[20px] border border-slate-200 dark:border-slate-800">
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
