'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';
import gsap from 'gsap';
import { 
  Sparkles, 
  Tag, 
  ShieldCheck, 
  Flame, 
  ArrowRight
} from 'lucide-react';

interface MarqueeItem {
  id: string;
  type: 'offer' | 'alert' | 'perk' | 'sustainability';
  badge: string;
  text: string;
  highlight?: string;
  link?: string;
  actionText?: string;
}

const MARQUEE_ITEMS: MarqueeItem[] = [
  {
    id: '1',
    type: 'offer',
    badge: 'AUTUMN SPECIAL',
    text: 'Early Bird Ridge Passes: Save 35% on certified Kalimpong & Rishop homestays',
    highlight: 'Code: YATRI35',
    link: '/destinations/darjeeling/alternatives',
    actionText: 'Claim Offer'
  },
  {
    id: '2',
    type: 'alert',
    badge: 'LIVE DECONGESTION',
    text: 'Darjeeling Tiger Hill currently congested (88/100). Recommending',
    highlight: 'Lava Pine Forest (18/100)',
    link: '/destinations/darjeeling/crowd',
    actionText: 'View Status'
  },
  {
    id: '3',
    type: 'perk',
    badge: 'COMMUNITY PERK',
    text: 'Zero Booking Fee + Complimentary organic breakfast on all Panchayat-verified cottages',
    highlight: '100% Direct Host Benefit',
    link: '/homestays',
    actionText: 'Browse Stays'
  },
  {
    id: '4',
    type: 'offer',
    badge: 'GROUP ADVENTURE',
    text: 'Book for 3+ guests to unlock private Neora Valley canopy guides & local permits',
    highlight: 'Save ₹1,200',
    link: '/itinerary',
    actionText: 'Plan Route'
  },
  {
    id: '5',
    type: 'sustainability',
    badge: 'ECO INCENTIVE',
    text: 'Travel off-peak and earn 500 EcoPoints redeemable on village tea estate tastings',
    highlight: 'Certified Sustainable',
    link: '/destinations',
    actionText: 'Learn More'
  }
];

export const TopMarquee: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!trackRef.current) return;

    // Use GSAP for smooth infinite looping
    const track = trackRef.current;
    const items = track.children;
    if (items.length === 0) return;

    // Calculate total width of half the items (original set)
    let totalWidth = 0;
    const halfCount = items.length / 2;
    for (let i = 0; i < halfCount; i++) {
      totalWidth += (items[i] as HTMLElement).offsetWidth;
    }

    if (totalWidth <= 0) return;

    const tween = gsap.to(track, {
      x: `-=${totalWidth}`,
      duration: 35,
      ease: 'none',
      repeat: -1,
      modifiers: {
        x: gsap.utils.unitize((x) => parseFloat(x) % totalWidth)
      }
    });

    // Pause on hover for accessibility and usability
    const onMouseEnter = () => tween.pause();
    const onMouseLeave = () => tween.play();

    const container = containerRef.current;
    if (container) {
      container.addEventListener('mouseenter', onMouseEnter);
      container.addEventListener('mouseleave', onMouseLeave);
    }

    return () => {
      tween.kill();
      if (container) {
        container.removeEventListener('mouseenter', onMouseEnter);
        container.removeEventListener('mouseleave', onMouseLeave);
      }
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      className="relative overflow-hidden bg-stone-950 text-stone-200 border-b border-stone-800/90 py-2.5 z-40 select-none"
    >
      {/* Subtle edge fade masks for high-end luxury feel */}
      <div className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-stone-950 to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-stone-950 to-transparent z-10 pointer-events-none" />

      <div 
        ref={trackRef}
        className="flex items-center gap-8 whitespace-nowrap will-change-transform cursor-pointer"
      >
        {/* Render items twice to allow seamless infinite loop */}
        {[...MARQUEE_ITEMS, ...MARQUEE_ITEMS].map((item, idx) => (
          <div 
            key={`${item.id}-${idx}`}
            className="flex items-center gap-3 text-xs tracking-tight shrink-0 px-2 group"
          >
            {/* Tag Badge */}
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider font-mono border ${
              item.type === 'offer'
                ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                : item.type === 'alert'
                ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                : item.type === 'perk'
                ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                : 'bg-sky-500/15 text-sky-300 border-sky-500/30'
            }`}>
              {item.type === 'offer' && <Tag className="w-2.5 h-2.5" />}
              {item.type === 'alert' && <Flame className="w-2.5 h-2.5" />}
              {item.type === 'perk' && <ShieldCheck className="w-2.5 h-2.5" />}
              {item.type === 'sustainability' && <Sparkles className="w-2.5 h-2.5" />}
              <span>{item.badge}</span>
            </span>

            {/* Content text */}
            <span className="text-stone-300 font-medium">
              {item.text}{' '}
              {item.highlight && (
                <strong className="text-amber-400 font-bold ml-1">{item.highlight}</strong>
              )}
            </span>

            {/* Action link */}
            {item.link && (
              <Link 
                href={item.link}
                className="inline-flex items-center gap-1 text-[11px] font-bold text-white group-hover:text-amber-300 underline underline-offset-4 decoration-stone-600 group-hover:decoration-amber-300 transition-colors ml-1"
              >
                <span>{item.actionText || 'Explore'}</span>
                <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
              </Link>
            )}

            {/* Separator diamond */}
            <span className="text-stone-700 mx-2 text-xs">◆</span>
          </div>
        ))}
      </div>
    </div>
  );
};
