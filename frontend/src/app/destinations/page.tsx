'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { DestinationSummary, CrowdLevel } from '@/types';
import { fetchDestinations } from '@/lib/api';
import { DestinationCard } from '@/components/DestinationCard';
import { Search, Flame, Filter, SlidersHorizontal, ArrowRight, Compass } from 'lucide-react';
import Link from 'next/link';

function DestinationsContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('query') || '';

  const [query, setQuery] = useState(initialQuery);
  const [selectedCrowd, setSelectedCrowd] = useState<string>('ALL');
  const [destinations, setDestinations] = useState<DestinationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const levelFilter = selectedCrowd === 'ALL' ? undefined : selectedCrowd;
      const data = await fetchDestinations(query || undefined, levelFilter);
      setDestinations(data);
      setLoading(false);
    }
    load();
  }, [query, selectedCrowd]);

  const crowdFilters = ['ALL', 'LOW', 'MEDIUM', 'HIGH', 'VERY HIGH'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-stone-200/80 dark:border-white/10">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-700 dark:text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">
            <Compass className="w-3.5 h-3.5" />
            <span>Curated Himalayan Sanctuary Catalog</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-stone-950 dark:text-white tracking-tight">
            Explore Himalayan Sanctuaries
          </h1>
          <p className="text-xs sm:text-sm text-stone-500 max-w-xl mt-2 leading-relaxed">
            Real-time multi-factor crowd intelligence and serene rural alternatives to help you choose low-impact, restorative journeys.
          </p>
        </div>

        {/* Demo Alert Banner */}
        <Link
          href="/destinations/darjeeling/crowd"
          className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 text-rose-700 dark:text-rose-400 text-xs font-bold hover:bg-rose-100/70 transition-all self-start md:self-auto shadow-xs"
        >
          <Flame className="w-4 h-4 animate-pulse" />
          <span>Demo: View Darjeeling (88/100 Overcrowded)</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Filter and Search Controls */}
      <div className="bg-white dark:bg-[#121824] p-5 rounded-3xl border border-stone-200/80 dark:border-white/10 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-stone-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter by name, tags e.g. 'Darjeeling', 'Monasteries', 'Orchids'..."
              className="w-full pl-11 pr-4 py-3 bg-stone-50 dark:bg-stone-900/90 rounded-2xl text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-amber-500 border border-stone-200/80 dark:border-white/10 text-stone-950 dark:text-white placeholder:text-stone-400"
            />
          </div>

          {/* Quick Clear */}
          {(query || selectedCrowd !== 'ALL') && (
            <button
              onClick={() => {
                setQuery('');
                setSelectedCrowd('ALL');
              }}
              className="text-xs font-bold text-stone-500 hover:text-stone-900 dark:hover:text-stone-200 px-3.5 py-2.5 rounded-xl hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Crowd Level Badges */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
          <span className="text-stone-400 font-bold uppercase tracking-wider text-[11px] flex items-center gap-1 shrink-0 mr-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Crowd Level:</span>
          </span>

          {crowdFilters.map((lvl) => (
            <button
              key={lvl}
              onClick={() => setSelectedCrowd(lvl)}
              className={`px-3.5 py-1.5 rounded-xl font-bold uppercase text-[11px] whitespace-nowrap transition-all ${
                selectedCrowd === lvl
                  ? 'bg-stone-950 dark:bg-white text-white dark:text-stone-950 shadow-xs'
                  : 'bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 hover:bg-stone-200/70 dark:hover:bg-stone-700'
              }`}
            >
              {lvl === 'ALL' ? 'All Densities' : lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Destination Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-96 bg-stone-200 dark:bg-stone-800 rounded-3xl" />
          ))}
        </div>
      ) : destinations.length === 0 ? (
        <div className="text-center py-20 bg-white dark:bg-[#121824] rounded-3xl border border-stone-200/80 dark:border-white/10 shadow-xs">
          <p className="text-stone-500 text-sm">No destinations found matching your criteria.</p>
          <button
            onClick={() => {
              setQuery('');
              setSelectedCrowd('ALL');
            }}
            className="mt-4 px-5 py-2.5 rounded-2xl bg-amber-700 hover:bg-amber-800 text-white text-xs font-bold transition-all shadow-xs"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {destinations.map((d) => (
            <DestinationCard key={d.id} destination={d} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function DestinationsPage() {
  return (
    <Suspense fallback={
      <div className="max-w-7xl mx-auto px-4 py-20 text-center text-stone-500">
        Loading sanctuaries...
      </div>
    }>
      <DestinationsContent />
    </Suspense>
  );
}

