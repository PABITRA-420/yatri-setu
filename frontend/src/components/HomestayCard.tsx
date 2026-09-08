import React from 'react';
import Link from 'next/link';
import { Homestay } from '@/types';
import { formatINR } from '@/lib/utils';
import { 
  Star, 
  ShieldCheck, 
  MapPin, 
  Check, 
  Sparkles, 
  HeartHandshake,
  CalendarCheck,
  Leaf,
  Award
} from 'lucide-react';

interface HomestayCardProps {
  homestay: Homestay;
  onBookClick?: (homestay: Homestay) => void;
}

export const HomestayCard: React.FC<HomestayCardProps> = ({ homestay, onBookClick }) => {
  const isPanchayatVerified = homestay.panchayat_verified ?? homestay.verified;
  const isHostVerified = homestay.host.verified_panchayat ?? true;
  const isSustainableStay = homestay.sustainable_stay_badge ?? true;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between group">
      <div>
        {/* Cover Photo */}
        <div className="relative h-52 w-full overflow-hidden">
          <img
            src={homestay.images[0]}
            alt={homestay.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/75 via-transparent to-transparent" />

          {/* Verification & Sustainability Badges Stack */}
          <div className="absolute top-3 left-3 flex flex-col gap-1.5 z-10">
            {isPanchayatVerified && (
              <div className="px-2.5 py-1 rounded-full bg-emerald-700/90 text-white font-bold text-[10px] tracking-wide backdrop-blur-md flex items-center gap-1 shadow-sm border border-emerald-400/30">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-300" />
                <span>PANCHAYAT VERIFIED</span>
              </div>
            )}
            {isHostVerified && (
              <div className="px-2 py-0.5 rounded-full bg-blue-700/90 text-white font-semibold text-[9px] tracking-wide backdrop-blur-md flex items-center gap-1 shadow-sm border border-blue-400/30">
                <Award className="w-3 h-3 text-blue-200" />
                <span>HOST VERIFIED</span>
              </div>
            )}
            {isSustainableStay && (
              <div className="px-2 py-0.5 rounded-full bg-teal-800/90 text-teal-100 font-semibold text-[9px] tracking-wide backdrop-blur-md flex items-center gap-1 shadow-sm border border-teal-400/30">
                <Leaf className="w-3 h-3 text-teal-300" />
                <span>SUSTAINABLE STAY</span>
              </div>
            )}
          </div>

          {/* Rating Badge */}
          <div className="absolute top-3 right-3">
            <div className="px-2.5 py-1 rounded-full bg-slate-900/80 text-white font-bold text-xs backdrop-blur-md flex items-center gap-1">
              <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
              <span>{homestay.rating}</span>
              <span className="text-[10px] text-slate-400">({homestay.reviews_count})</span>
            </div>
          </div>

          {/* Location Bottom Left */}
          <div className="absolute bottom-3 left-3 text-white text-xs font-semibold flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span>{homestay.destination_name}</span>
          </div>
        </div>

        {/* Content Details */}
        <div className="p-5">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-extrabold text-base text-slate-900 dark:text-white line-clamp-1">
                {homestay.title}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1">
                {homestay.tagline}
              </p>
            </div>
          </div>

          {/* Host Mini Profile */}
          <div className="flex items-center gap-2.5 mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <img
              src={homestay.host.avatar_url}
              alt={homestay.host.name}
              className="w-9 h-9 rounded-full object-cover border border-amber-500/30"
            />
            <div className="text-xs">
              <span className="font-bold text-slate-900 dark:text-white block leading-none">
                Hosted by {homestay.host.name}
              </span>
              <span className="text-[10px] text-slate-400">
                {homestay.host.experience_years} yrs hosting • {homestay.host.languages.slice(0, 2).join(', ')}
              </span>
            </div>
          </div>

          {/* Signature Activity */}
          <div className="mt-3 p-2.5 rounded-xl bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 text-xs">
            <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-amber-600 dark:text-amber-400">
              <Sparkles className="w-3 h-3" />
              <span>Host Experience Included</span>
            </div>
            <p className="text-slate-700 dark:text-slate-300 font-medium text-[11px] mt-0.5">
              {homestay.special_activity}
            </p>
          </div>

          {/* Community Fund Banner */}
          <div className="mt-2.5 flex items-center gap-1.5 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400">
            <HeartHandshake className="w-3.5 h-3.5 shrink-0" />
            <span>{homestay.community_fund_contribution_percent}% contributes to local village development fund</span>
          </div>

          {/* Amenities preview */}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {homestay.amenities.slice(0, 3).map((amenity, i) => (
              <span
                key={i}
                className="text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded"
              >
                {amenity}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footer / Price and CTA */}
      <div className="px-5 pb-5 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-baseline gap-1">
            <span className="font-extrabold text-base text-slate-900 dark:text-white">
              {formatINR(homestay.price_per_night_inr)}
            </span>
            <span className="text-xs text-slate-400">/ night</span>
          </div>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium block">
            Direct host payment
          </span>
        </div>

        <Link
          href={`/booking/confirmation?homestay_id=${homestay.id}`}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-xs shadow-md shadow-amber-600/20 active:scale-95 transition-all"
        >
          <CalendarCheck className="w-4 h-4" />
          <span>Reserve Stay</span>
        </Link>
      </div>
    </div>
  );
};
