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
    <div className="neo-card group relative flex flex-col justify-between rounded-3xl bg-white dark:bg-[#121824] border border-stone-200/80 dark:border-white/10 overflow-hidden">
      <div>
        {/* Visual Cover with Subtle Zoom */}
        <div className="relative h-60 sm:h-64 w-full overflow-hidden bg-stone-900">
          <img
            src={destination.hero_image}
            alt={destination.name}
            className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105 filter brightness-[0.96] group-hover:brightness-100"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-stone-950/80 via-stone-950/20 to-transparent" />

          {/* Crowd Tag Top Right - Controlled Glass Pill */}
          <div className="absolute top-3.5 right-3.5">
            <div className={`glass-pill px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5 shadow-sm ${badge.text}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
              <span>{destination.crowd_score}/100 {destination.crowd_level}</span>
            </div>
          </div>

          {/* Region & State Overlay */}
          <div className="absolute bottom-3.5 left-4 flex items-center gap-1 text-white text-xs font-medium tracking-wide">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span className="drop-shadow-sm">{destination.region}, {destination.state}</span>
          </div>
        </div>

        {/* Content Section */}
        <div className="p-6">
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="font-extrabold text-xl text-stone-950 dark:text-white tracking-tight group-hover:text-amber-700 dark:group-hover:text-amber-400 transition-colors">
              {destination.name}
            </h3>
          </div>

          <p className="text-xs text-stone-500 dark:text-stone-400 mt-1.5 line-clamp-2 leading-relaxed">
            {destination.tagline}
          </p>

          {/* Smart Information Chips */}
          <div className="flex flex-wrap gap-1.5 mt-4">
            {destination.tags.map((tag) => (
              <span
                key={tag}
                className="text-[10px] font-semibold bg-stone-100 dark:bg-stone-800/80 text-stone-600 dark:text-stone-300 px-2.5 py-1 rounded-md border border-stone-200/60 dark:border-white/5"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footer / Price & Clean Action Buttons */}
      <div className="px-6 pb-6 pt-3 border-t border-stone-100 dark:border-white/5 flex items-center justify-between">
        <div>
          <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block">
            Avg Daily Budget
          </span>
          <span className="font-bold text-sm text-stone-950 dark:text-white font-mono">
            {formatINR(destination.avg_cost_per_day_inr)}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href={`/destinations/${destination.id}/crowd`}
            className="p-2.5 rounded-xl bg-stone-100 dark:bg-stone-800 hover:bg-amber-100/60 dark:hover:bg-amber-950/40 text-stone-600 dark:text-stone-300 hover:text-amber-700 dark:hover:text-amber-400 transition-all border border-stone-200/80 dark:border-white/10"
            title="Check Crowd Heatmap"
          >
            <Flame className="w-4 h-4" />
          </Link>

          <Link
            href={`/destinations/${destination.id}`}
            className="btn-neo-primary flex items-center gap-1.5 px-4 py-2 text-xs font-bold transition-all"
          >
            <span>Explore</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
};

