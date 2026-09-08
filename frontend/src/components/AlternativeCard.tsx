import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { AlternativeRecommendation } from '@/types';
import { getCrowdBadgeStyle, formatINR } from '@/lib/utils';
import { 
  Sparkles, 
  MapPin, 
  TrendingDown, 
  CheckCircle, 
  ArrowRight, 
  ShieldCheck,
  Compass
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
    <div className="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-all duration-300 group">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-0">
        {/* Left: Visual & Highlights */}
        <div className="lg:col-span-5 relative min-h-[240px] lg:min-h-full">
          <img
            src={alternative.hero_image}
            alt={alternative.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-950/20 to-transparent" />

          {/* Similarity & Eco Badges */}
          <div className="absolute top-4 left-4 flex flex-wrap gap-2">
            <div className="px-3 py-1 rounded-full bg-emerald-600/90 text-white font-black text-xs backdrop-blur-md flex items-center gap-1.5 shadow-lg">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>{alternative.similarity_score}% SIMILARITY</span>
            </div>
            <div className="px-2.5 py-1 rounded-full bg-slate-900/80 text-white font-medium text-[11px] backdrop-blur-md border border-white/10">
              {alternative.eco_tag}
            </div>
          </div>

          {/* Bottom Overlay Info */}
          <div className="absolute bottom-4 left-4 right-4 text-white">
            <div className="flex items-center gap-1 text-xs text-amber-300 font-semibold mb-1">
              <MapPin className="w-3.5 h-3.5" />
              <span>{alternative.distance_km} km from {originName}</span>
            </div>
            <h3 className="text-2xl font-black tracking-tight">{alternative.name}</h3>
            <p className="text-xs text-slate-200 line-clamp-2 mt-0.5">
              {alternative.tagline}
            </p>
          </div>
        </div>

        {/* Right: Metrics & Why Recommend */}
        <div className="lg:col-span-7 p-6 flex flex-col justify-between">
          <div>
            {/* Metric Chips Row */}
            <div className="grid grid-cols-3 gap-3 pb-4 mb-4 border-b border-slate-100 dark:border-slate-800">
              {/* Metric 1: Crowd Score */}
              <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-xl text-center">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                  Crowd Score
                </span>
                <div className="flex items-center justify-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${crowdBadge.dot}`} />
                  <span className="font-extrabold text-sm text-slate-900 dark:text-white">
                    {alternative.crowd_score}
                  </span>
                  <span className="text-[10px] text-slate-400">/100</span>
                </div>
                <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 block mt-0.5">
                  ↓ {alternative.crowd_reduction_percent || Math.round(((alternative.original_crowd_score || 88) - alternative.crowd_score) / (alternative.original_crowd_score || 88) * 100)}% Lower Crowd
                </span>
              </div>

              {/* Metric 2: Estimated Cost */}
              <div className="bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-xl text-center">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                  Avg Cost / Day
                </span>
                <span className="font-extrabold text-sm text-slate-900 dark:text-white block">
                  {formatINR(alternative.estimated_cost_per_day)}
                </span>
                <span className="text-[10px] text-slate-400">per person</span>
              </div>

              {/* Metric 3: Cost Savings */}
              <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500/20 p-2.5 rounded-xl text-center">
                <span className="text-[10px] uppercase font-bold text-emerald-600 dark:text-emerald-400 block mb-0.5">
                  Cost Savings
                </span>
                <div className="flex items-center justify-center gap-1 text-emerald-600 dark:text-emerald-400 font-extrabold text-sm">
                  <TrendingDown className="w-3.5 h-3.5" />
                  <span>{Math.abs(alternative.cost_difference_percent)}% Less</span>
                </div>
                <span className="text-[10px] text-emerald-700 dark:text-emerald-500">
                  vs. {originName}
                </span>
              </div>
            </div>

            {/* Matching Attributes Chips */}
            {alternative.matching_attributes && alternative.matching_attributes.length > 0 && (
              <div className="mb-3.5 flex flex-wrap items-center gap-1.5">
                <span className="text-[10px] font-bold uppercase text-slate-400 mr-1">
                  Matching Charms:
                </span>
                {alternative.matching_attributes.map((attr, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded-md border border-slate-200/60 dark:border-slate-700/60"
                  >
                    ✓ {attr}
                  </span>
                ))}
              </div>
            )}

            {/* Why Yatri Setu Recommends This Section */}
            <div className="mb-4">
              <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-500 mb-2">
                <ShieldCheck className="w-4 h-4" />
                <span>Why Yatri Setu Recommends This:</span>
              </div>
              <ul className="space-y-2">
                {alternative.reasons_to_recommend.map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-300">
                    <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Key Experience */}
            <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 mb-4">
              <span className="text-[10px] uppercase font-bold text-amber-600 dark:text-amber-400 block">
                Signature Experience
              </span>
              <p className="text-xs font-medium text-slate-800 dark:text-slate-200 mt-0.5">
                {alternative.key_experience}
              </p>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
            <Link
              href={`/itinerary?destination=${alternative.id}`}
              className="w-full sm:w-auto flex-1 flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-xs shadow-md shadow-amber-600/20 active:scale-98 transition-all"
            >
              <span>Choose {alternative.name} & Generate Itinerary</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href={`/destinations/${alternative.id}`}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-semibold transition-colors text-center"
            >
              Explore Details
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
