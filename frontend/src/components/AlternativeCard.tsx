import React from 'react';
import Link from 'next/link';
import { AlternativeRecommendation } from '@/types';
import { getCrowdBadgeStyle, formatINR } from '@/lib/utils';
import { 
  Sparkles, 
  MapPin, 
  TrendingDown, 
  CheckCircle, 
  ArrowRight, 
  ShieldCheck,
  Compass,
  ArrowUpRight
} from 'lucide-react';

interface AlternativeCardProps {
  alternative: AlternativeRecommendation;
  originName: string;
}

export const AlternativeCard: React.FC<AlternativeCardProps> = ({
  alternative,
  originName
}) => {
  const crowdBadge = getCrowdBadgeStyle(alternative.crowd_level);

  return (
    <div className="editorial-card group rounded-3xl overflow-hidden bg-white dark:bg-[#121824] border border-stone-200/80 dark:border-white/10 shadow-xs hover:shadow-md transition-all duration-300">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-0">
        {/* Left: Visual & Highlights */}
        <div className="lg:col-span-5 relative min-h-[260px] lg:min-h-full overflow-hidden bg-stone-900">
          <img
            src={alternative.hero_image}
            alt={alternative.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out filter brightness-[0.92]"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-stone-950/90 via-stone-950/30 to-transparent" />

          {/* Similarity & Eco Badges */}
          <div className="absolute top-4 left-4 flex flex-wrap gap-2 z-10">
            <div className="glass-pill px-3 py-1 rounded-full text-stone-900 dark:text-white font-extrabold text-xs flex items-center gap-1.5 shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
              <span>{alternative.similarity_score}% SIMILARITY</span>
            </div>
            {alternative.eco_tag && (
              <div className="glass-pill px-2.5 py-0.5 rounded-full text-stone-800 dark:text-stone-200 font-semibold text-[10px] shadow-sm">
                {alternative.eco_tag}
              </div>
            )}
          </div>

          {/* Bottom Overlay Info */}
          <div className="absolute bottom-4 left-4 right-4 text-white">
            <div className="flex items-center gap-1 text-xs text-amber-300 font-medium mb-1">
              <MapPin className="w-3.5 h-3.5" />
              <span>{alternative.distance_km} km from {originName}</span>
            </div>
            <h3 className="text-2xl font-extrabold tracking-tight">{alternative.name}</h3>
            <p className="text-xs text-stone-200 line-clamp-2 mt-0.5 leading-relaxed">
              {alternative.tagline}
            </p>
          </div>
        </div>

        {/* Right: Metrics & Why Recommend */}
        <div className="lg:col-span-7 p-6 sm:p-8 flex flex-col justify-between">
          <div>
            {/* Metric Chips Row */}
            <div className="grid grid-cols-3 gap-3 pb-5 mb-5 border-b border-stone-100 dark:border-white/5">
              {/* Metric 1: Crowd Score */}
              <div className="bg-stone-50 dark:bg-stone-900/60 p-3 rounded-2xl border border-stone-200/60 dark:border-white/5 text-center">
                <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block mb-0.5">
                  Crowd Index
                </span>
                <div className="flex items-center justify-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${crowdBadge.dot}`} />
                  <span className="font-extrabold text-base text-stone-950 dark:text-white font-mono">
                    {alternative.crowd_score}
                  </span>
                  <span className="text-[10px] text-stone-400">/100</span>
                </div>
                <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 block mt-0.5">
                  ↓ {alternative.crowd_reduction_percent || Math.round(((alternative.original_crowd_score || 88) - alternative.crowd_score) / (alternative.original_crowd_score || 88) * 100)}% Lower
                </span>
              </div>

              {/* Metric 2: Estimated Cost */}
              <div className="bg-stone-50 dark:bg-stone-900/60 p-3 rounded-2xl border border-stone-200/60 dark:border-white/5 text-center">
                <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider block mb-0.5">
                  Avg Cost / Day
                </span>
                <span className="font-extrabold text-base text-stone-950 dark:text-white font-mono block">
                  {formatINR(alternative.estimated_cost_per_day)}
                </span>
                <span className="text-[10px] text-stone-400">per person</span>
              </div>

              {/* Metric 3: Cost Savings */}
              <div className="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-500/20 p-3 rounded-2xl text-center">
                <span className="text-[10px] uppercase font-bold text-emerald-700 dark:text-emerald-400 tracking-wider block mb-0.5">
                  Cost Savings
                </span>
                <div className="flex items-center justify-center gap-1 text-emerald-700 dark:text-emerald-400 font-extrabold text-base font-mono">
                  <TrendingDown className="w-4 h-4" />
                  <span>{Math.abs(alternative.cost_difference_percent)}% Less</span>
                </div>
                <span className="text-[10px] text-emerald-700/80 dark:text-emerald-500">
                  vs. {originName}
                </span>
              </div>
            </div>

            {/* Matching Attributes Chips */}
            {alternative.matching_attributes && alternative.matching_attributes.length > 0 && (
              <div className="mb-4 flex flex-wrap items-center gap-1.5">
                <span className="text-[10px] font-bold uppercase text-stone-400 tracking-wider mr-1">
                  Shared Charms:
                </span>
                {alternative.matching_attributes.map((attr, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] font-semibold bg-stone-100 dark:bg-stone-800/80 text-stone-700 dark:text-stone-300 px-2.5 py-1 rounded-md border border-stone-200/60 dark:border-white/5"
                  >
                    {attr}
                  </span>
                ))}
              </div>
            )}

            {/* Why Yatri Setu Recommends */}
            {alternative.reasons_to_recommend && alternative.reasons_to_recommend.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400 mb-2">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Why Yatri Setu Recommends This:</span>
                </div>
                <ul className="space-y-1.5">
                  {alternative.reasons_to_recommend.map((reason, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs text-stone-600 dark:text-stone-300">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Key Experience */}
            {alternative.key_experience && (
              <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-3.5 mb-4">
                <span className="text-[10px] uppercase font-bold text-amber-700 dark:text-amber-400 tracking-wider block">
                  Signature Experience
                </span>
                <p className="text-xs font-medium text-stone-800 dark:text-stone-200 mt-1">
                  {alternative.key_experience}
                </p>
              </div>
            )}
          </div>

          {/* Action Row */}
          <div className="pt-4 border-t border-stone-100 dark:border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3">
            <Link
              href={`/destinations/${alternative.id}`}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-stone-200 dark:border-white/10 hover:bg-stone-100 dark:hover:bg-stone-800 text-xs font-bold text-stone-800 dark:text-stone-200 transition-colors text-center"
            >
              Explore Details
            </Link>

            <Link
              href={`/itinerary?destination=${alternative.id}`}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-stone-950 dark:bg-white text-white dark:text-stone-950 hover:bg-amber-700 dark:hover:bg-amber-400 dark:hover:text-stone-950 text-xs font-bold shadow-xs active:scale-97 transition-all"
            >
              <span>Choose {alternative.name} & Generate Itinerary</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
