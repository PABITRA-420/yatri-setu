import React from 'react';
import Link from 'next/link';
import { DestinationSummary } from '@/types';
import { getCrowdBadgeStyle, formatINR } from '@/lib/utils';
import { MapPin, ArrowUpRight, Flame } from 'lucide-react';

interface DestinationCardProps {
  destination: DestinationSummary;
}

export const DestinationCard: React.FC<DestinationCardProps> = ({ destination }) => {
  const badge = getCrowdBadgeStyle(destination.crowd_level);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-lg transition-all duration-300 group flex flex-col justify-between">
      <div>
        {/* Visual Cover */}
        <div className="relative h-48 sm:h-52 w-full overflow-hidden">
          <img
            src={destination.hero_image}
            alt={destination.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-transparent to-transparent" />

          {/* Crowd Tag Top Right */}
          <div className="absolute top-3 right-3">
            <div className={`px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider backdrop-blur-md border flex items-center gap-1.5 shadow-md ${badge.bg} ${badge.border}`}>
              <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
              <span>{destination.crowd_score}/100 {destination.crowd_level}</span>
            </div>
          </div>

          {/* State / Region bottom left */}
          <div className="absolute bottom-3 left-3 flex items-center gap-1 text-white text-xs font-semibold">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span>{destination.region}, {destination.state}</span>
          </div>
        </div>

        {/* Content */}
        <div className="p-5">
          <h3 className="font-extrabold text-lg text-slate-900 dark:text-white tracking-tight group-hover:text-amber-600 transition-colors">
            {destination.name}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
            {destination.tagline}
          </p>

          {/* Tags */}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {destination.tags.map((tag) => (
              <span
                key={tag}
                className="text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-md"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footer / Price & Link */}
      <div className="px-5 pb-5 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
        <div>
          <span className="text-[10px] uppercase font-bold text-slate-400 block">
            Avg Daily Budget
          </span>
          <span className="font-bold text-sm text-slate-900 dark:text-white">
            {formatINR(destination.avg_cost_per_day_inr)}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href={`/destinations/${destination.id}/crowd`}
            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-amber-50 dark:hover:bg-amber-950/40 text-slate-600 hover:text-amber-600 transition-colors"
            title="Check Crowd Heatmap"
          >
            <Flame className="w-4 h-4" />
          </Link>

          <Link
            href={`/destinations/${destination.id}`}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-amber-600 dark:hover:bg-amber-500 dark:hover:text-white text-xs font-bold transition-all"
          >
            <span>Explore</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
};
