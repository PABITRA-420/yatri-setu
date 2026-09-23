'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Homestay } from '@/types';
import { formatINR } from '@/lib/utils';
import { 
  Star, 
  ShieldCheck, 
  MapPin, 
  Sparkles, 
  HeartHandshake,
  CalendarCheck,
  Leaf,
  ChevronLeft,
  ChevronRight,
  Eye
} from 'lucide-react';

interface HomestayCardProps {
  homestay: Homestay;
  onQuickView?: (homestay: Homestay) => void;
}

export const HomestayCard: React.FC<HomestayCardProps> = ({ homestay, onQuickView }) => {
  const [currentImageIdx, setCurrentImageIdx] = useState(0);

  const images = homestay.images && homestay.images.length > 0 ? homestay.images : ['https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1200&q=80'];
  const isPanchayatVerified = homestay.panchayat_verified ?? homestay.verified;
  const isSustainableStay = homestay.sustainable_stay_badge ?? true;

  const nextImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    setCurrentImageIdx((prev) => (prev + 1) % images.length);
  };

  const prevImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    setCurrentImageIdx((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <div className="neo-card group relative flex flex-col justify-between rounded-3xl bg-white dark:bg-[#121824] border border-stone-200/80 dark:border-white/10 overflow-hidden hover:border-amber-500/40 hover:-translate-y-1 transition-all duration-300">
      <div>
        {/* Cover Photography & Carousel */}
        <div className="relative h-60 w-full overflow-hidden bg-stone-900 group/img">
          <img
            src={images[currentImageIdx]}
            alt={homestay.title}
            className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105 filter brightness-[0.95] group-hover:brightness-100"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-stone-950/80 via-stone-950/20 to-transparent" />

          {/* Carousel Arrows */}
          {images.length > 1 && (
            <>
              <button
                onClick={prevImage}
                className="absolute left-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-stone-950/60 text-white opacity-0 group-hover/img:opacity-100 hover:bg-amber-500 transition-all z-20"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-stone-950/60 text-white opacity-0 group-hover/img:opacity-100 hover:bg-amber-500 transition-all z-20"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
              {/* Dots */}
              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-1 z-20">
                {images.map((_, idx) => (
                  <span
                    key={idx}
                    className={`h-1.5 rounded-full transition-all ${
                      idx === currentImageIdx ? 'w-4 bg-amber-400' : 'w-1.5 bg-white/50'
                    }`}
                  />
                ))}
              </div>
            </>
          )}

          {/* Verification & Badges Stack */}
          <div className="absolute top-3.5 left-3.5 flex flex-col gap-1.5 z-10">
            {isPanchayatVerified && (
              <div className="glass-pill px-3 py-1 rounded-full text-emerald-400 font-bold text-[10px] tracking-wider uppercase flex items-center gap-1.5 shadow-sm bg-emerald-950/80 border border-emerald-500/40">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Panchayat Verified</span>
              </div>
            )}
            {isSustainableStay && (
              <div className="glass-pill px-2.5 py-0.5 rounded-full text-stone-300 font-semibold text-[9px] tracking-wide flex items-center gap-1 shadow-sm bg-stone-900/80 border border-white/10">
                <Leaf className="w-3 h-3 text-emerald-400" />
                <span>Sustainable</span>
              </div>
            )}
          </div>

          {/* Rating Badge */}
          <div className="absolute top-3.5 right-3.5 z-10">
            <div className="glass-pill px-3 py-1 rounded-full text-white font-bold text-xs flex items-center gap-1.5 shadow-sm bg-stone-900/80 border border-white/10">
              <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
              <span>{homestay.rating}</span>
              <span className="text-[10px] text-stone-400">({homestay.reviews_count})</span>
            </div>
          </div>

          {/* Destination Overlay */}
          <div className="absolute bottom-3.5 left-4 text-white text-xs font-medium flex items-center gap-1 z-10">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span className="drop-shadow-sm">{homestay.destination_name}</span>
          </div>
        </div>

        {/* Content Details */}
        <div className="p-6">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-extrabold text-lg text-stone-950 dark:text-white group-hover:text-amber-400 transition-colors line-clamp-1">
              {homestay.title}
            </h3>
            {onQuickView && (
              <button
                onClick={() => onQuickView(homestay)}
                className="p-1.5 rounded-xl bg-stone-100 dark:bg-stone-800 text-stone-400 hover:text-amber-400 hover:bg-amber-500/10 transition-colors shrink-0"
                title="Quick View Host Details"
              >
                <Eye className="w-4 h-4" />
              </button>
            )}
          </div>

          <p className="text-xs text-stone-500 dark:text-stone-400 mt-1 line-clamp-1 leading-relaxed">
            {homestay.tagline}
          </p>

          {/* Host Profile */}
          <div className="flex items-center gap-3 mt-4 pt-4 border-t border-stone-100 dark:border-white/5">
            <img
              src={homestay.host.avatar_url}
              alt={homestay.host.name}
              className="w-10 h-10 rounded-full object-cover border border-stone-200 dark:border-white/10"
              loading="lazy"
            />
            <div className="text-xs">
              <span className="font-bold text-stone-900 dark:text-white block leading-tight">
                Hosted by {homestay.host.name}
              </span>
              <span className="text-[10px] text-stone-400 block mt-0.5">
                {homestay.host.languages.slice(0, 2).join(', ')}
              </span>
            </div>
          </div>

          {/* Signature Activity */}
          <div className="mt-3 p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs">
            <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-amber-400">
              <Sparkles className="w-3 h-3" />
              <span>Host Experience Included</span>
            </div>
            <p className="text-stone-300 font-medium text-[11px] mt-0.5">
              {homestay.special_activity}
            </p>
          </div>

          {/* Community Fund Banner */}
          <div className="mt-2.5 flex items-center gap-1.5 text-[11px] font-semibold text-emerald-400">
            <HeartHandshake className="w-3.5 h-3.5 shrink-0" />
            <span>{homestay.community_fund_contribution_percent}% contributes to local village development fund</span>
          </div>

          {/* Amenities preview */}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {homestay.amenities.slice(0, 3).map((amenity, i) => (
              <span
                key={i}
                className="text-[10px] bg-stone-800 text-stone-300 px-2 py-0.5 rounded-md border border-white/5"
              >
                {amenity}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footer / Price and CTA */}
      <div className="px-6 pb-6 pt-3 border-t border-stone-100 dark:border-white/5 flex items-center justify-between">
        <div>
          <div className="flex items-baseline gap-1">
            <span className="font-extrabold text-base text-stone-950 dark:text-white font-mono">
              {formatINR(homestay.price_per_night_inr)}
            </span>
            <span className="text-xs text-stone-400">/ night</span>
          </div>
          <span className="text-[10px] text-emerald-400 font-medium block">
            Direct host payment
          </span>
        </div>

        <div className="flex items-center gap-2">
          {onQuickView && (
            <button
              onClick={() => onQuickView(homestay)}
              className="px-3 py-2 rounded-xl bg-stone-800 hover:bg-stone-700 text-stone-200 text-xs font-bold transition-all border border-white/10"
            >
              Quick View
            </button>
          )}

          <Link
            href={`/booking/confirmation?homestay_id=${homestay.id}`}
            className="btn-neo-primary flex items-center gap-1.5 px-4 py-2.5 text-xs font-bold transition-all shadow-md active:scale-95"
          >
            <CalendarCheck className="w-3.5 h-3.5" />
            <span>Reserve</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
