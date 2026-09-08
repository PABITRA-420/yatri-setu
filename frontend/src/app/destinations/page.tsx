'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { DestinationSummary, CrowdLevel } from '@/types';
import { fetchDestinations } from '@/lib/api';
import { DestinationCard } from '@/components/DestinationCard';
import { Search, Flame, Filter, SlidersHorizontal, ArrowRight } from 'lucide-react';
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Explore Himalayan Sanctuaries
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time crowd intelligence and low-density rural alternatives
          </p>
        </div>

        {/* Highlight Banner */}
        <Link
          href="/destinations/darjeeling/crowd"
          className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 text-xs font-bold hover:bg-rose-500/20 transition-all self-start md:self-auto"
        >
          <Flame className="w-4 h-4 animate-pulse" />
          <span>Demo: View Darjeeling (88/100 Overcrowded)</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Filter and Search Controls */}
      <div className="bg-white dark:bg-slate-900 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter by name, tags e.g. 'Darjeeling', 'Monasteries', 'Orchids'..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 border border-slate-200 dark:border-slate-700"
            />
          </div>

          {/* Quick Clear */}
          {(query || selectedCrowd !== 'ALL') && (
            <button
              onClick={() => {
                setQuery('');
                setSelectedCrowd('ALL');
              }}
              className="text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 px-3 py-2"
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Crowd Level Badges */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
          <span className="text-slate-400 font-semibold flex items-center gap-1 shrink-0">
            <Filter className="w-3.5 h-3.5" />
            <span>Crowd Level:</span>
          </span>

          {crowdFilters.map((lvl) => (
            <button
              key={lvl}
              onClick={() => setSelectedCrowd(lvl)}
              className={`px-3 py-1.5 rounded-xl font-bold uppercase text-[11px] whitespace-nowrap transition-all ${
                selectedCrowd === lvl
                  ? 'bg-amber-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
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
            <div key={i} className="h-80 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          ))}
        </div>
      ) : destinations.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
          <p className="text-slate-500 text-sm">No destinations found matching your criteria.</p>
          <button
            onClick={() => {
              setQuery('');
              setSelectedCrowd('ALL');
            }}
            className="mt-3 px-4 py-2 rounded-xl bg-amber-600 text-white text-xs font-bold"
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
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading destinations...
      </div>
    }>
      <DestinationsContent />
    </Suspense>
  );
}
