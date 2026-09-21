'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import {
  Mountain,
  Trees,
  Landmark,
  Footprints,
  Home as HomeIcon,
  Camera,
  ArrowRight,
  ArrowUpRight,
  MoveHorizontal,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '@/lib/utils';

interface HimalayanTheme {
  id: string;
  num: string;
  title: string;
  desc: string;
  tags: string[];
  query: string;
  icon: React.ComponentType<{ className?: string }>;
  image: string;
}

const THEMES: HimalayanTheme[] = [
  {
    id: 'mountains-ridges',
    num: '01',
    title: 'Mountains & Ridges',
    desc: 'High-altitude panoramas, dramatic ridgelines and quieter viewpoints.',
    tags: ['HIGH ALTITUDE', 'SCENIC', 'LOW CROWD'],
    query: 'mountains',
    icon: Mountain,
    image:
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=85',
  },
  {
    id: 'pine-woodlands',
    num: '02',
    title: 'Pine Woodlands',
    desc: 'Misty forests, canopy walks and slow days surrounded by nature.',
    tags: ['FOREST', 'QUIET', 'NATURE'],
    query: 'nature',
    icon: Trees,
    image:
      'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1600&q=85',
  },
  {
    id: 'heritage-monasteries',
    num: '03',
    title: 'Heritage & Monasteries',
    desc: 'Ancient gompas, mountain traditions and living Himalayan culture.',
    tags: ['CULTURE', 'MONASTERIES', 'LOCAL LIFE'],
    query: 'monasteries',
    icon: Landmark,
    image:
      'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1600&q=85',
  },
  {
    id: 'alpine-trails',
    num: '04',
    title: 'Alpine Trails',
    desc: 'Highland trails, village routes and guided mountain experiences.',
    tags: ['TREKKING', 'GUIDED', 'ADVENTURE'],
    query: 'trails',
    icon: Footprints,
    image:
      'https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=1600&q=85',
  },
  {
    id: 'panchayat-homestays',
    num: '05',
    title: 'Panchayat Homestays',
    desc: 'Stay locally, meet hosts and keep more of your journey within the community.',
    tags: ['LOCAL HOST', 'COMMUNITY', 'AUTHENTIC'],
    query: 'homestays',
    icon: HomeIcon,
    image:
      'https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=1600&q=85',
  },
  {
    id: 'flora-photography',
    num: '06',
    title: 'Flora & Photography',
    desc: 'Orchids, cloud-filled valleys and landscapes made for slow exploration.',
    tags: ['ORCHIDS', 'SUNRISE', 'PHOTO SPOTS'],
    query: 'orchids',
    icon: Camera,
    image:
      'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1600&q=85',
  },
];

export default function HimalayanThemesGallery() {
  const [activeIdx, setActiveIdx] = useState<number>(0);
  const [hasInteracted, setHasInteracted] = useState<boolean>(false);
  const [parallax, setParallax] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);
  const [dragOffset, setDragOffset] = useState<number>(0);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const dragStartXRef = useRef<number>(0);
  const isPointerDownRef = useRef<boolean>(false);
  const mobileScrollRef = useRef<HTMLDivElement>(null);
  const galleryRef = useRef<HTMLDivElement>(null);

  // Check prefers-reduced-motion
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mq.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  // Subtle image parallax on active card (max 8-10px)
  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>, index: number) => {
      if (prefersReducedMotion || index !== activeIdx) return;
      const rect = e.currentTarget.getBoundingClientRect();
      const relX = (e.clientX - rect.left) / rect.width - 0.5;
      const relY = (e.clientY - rect.top) / rect.height - 0.5;
      setParallax({
        x: Math.round(relX * 18), // max ~9px
        y: Math.round(relY * 18),
      });
    },
    [activeIdx, prefersReducedMotion]
  );

  const handleMouseLeave = useCallback(() => {
    setParallax({ x: 0, y: 0 });
  }, []);

  // Pointer drag for Desktop
  const handlePointerDown = (e: React.PointerEvent) => {
    if (e.button !== 0) return;
    isPointerDownRef.current = true;
    dragStartXRef.current = e.clientX;
    setIsDragging(true);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isPointerDownRef.current) return;
    const diff = e.clientX - dragStartXRef.current;
    // apply elastic resistance
    setDragOffset(diff * 0.22);
  };

  const handlePointerEnd = (e: React.PointerEvent) => {
    if (!isPointerDownRef.current) return;
    isPointerDownRef.current = false;
    setIsDragging(false);

    const diff = e.clientX - dragStartXRef.current;
    const threshold = 50; // drag threshold to switch

    if (diff < -threshold && activeIdx < THEMES.length - 1) {
      setActiveIdx((prev) => prev + 1);
      setHasInteracted(true);
    } else if (diff > threshold && activeIdx > 0) {
      setActiveIdx((prev) => prev - 1);
      setHasInteracted(true);
    }

    setDragOffset(0);
  };

  // Mobile scroll observer to update active indicator
  const handleMobileScroll = () => {
    if (!mobileScrollRef.current) return;
    setHasInteracted(true);
    const container = mobileScrollRef.current;
    const scrollLeft = container.scrollLeft;
    const itemWidth = container.clientWidth * 0.82;
    const newIdx = Math.min(
      THEMES.length - 1,
      Math.max(0, Math.round(scrollLeft / itemWidth))
    );
    if (newIdx !== activeIdx) {
      setActiveIdx(newIdx);
    }
  };

  const scrollMobileTo = (index: number) => {
    setActiveIdx(index);
    setHasInteracted(true);
    if (mobileScrollRef.current) {
      const container = mobileScrollRef.current;
      const card = container.children[index] as HTMLElement;
      if (card) {
        card.scrollIntoView({
          behavior: prefersReducedMotion ? 'auto' : 'smooth',
          inline: 'center',
          block: 'nearest',
        });
      }
    }
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const nextIdx = Math.min(THEMES.length - 1, index + 1);
      setActiveIdx(nextIdx);
      setHasInteracted(true);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prevIdx = Math.max(0, index - 1);
      setActiveIdx(prevIdx);
      setHasInteracted(true);
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setActiveIdx(index);
      setHasInteracted(true);
    }
  };

  const currentTheme = THEMES[activeIdx];

  return (
    <section
      className="relative w-full py-18 lg:py-24 z-10 overflow-hidden"
      aria-label="Curated Escapes: Find Your Himalayan Rhythm"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* ==================================================
            SECTION HEADER
            ================================================== */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12 pb-6 border-b border-stone-200 dark:border-stone-800/80">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-2"
          >
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
              <span className="text-xs font-extrabold uppercase tracking-widest text-amber-700 dark:text-amber-400 font-mono">
                CURATED ESCAPES
              </span>
            </div>
            <h2 className="text-3xl sm:text-5xl lg:text-5xl font-extrabold text-stone-950 dark:text-white tracking-tight leading-tight">
              FIND YOUR HIMALAYAN RHYTHM
            </h2>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col sm:flex-row md:items-end gap-6 md:gap-10"
          >
            <p className="text-sm sm:text-base text-stone-600 dark:text-stone-400 max-w-md leading-relaxed">
              From high-altitude ridges to quiet forests and living heritage, discover
              the side of the Himalayas that matches the way you travel.
            </p>

            {/* Subtle Counter 01 / 06 with vertical roll */}
            <div
              className="flex items-baseline font-mono self-start sm:self-auto bg-stone-100 dark:bg-stone-900/80 px-4 py-2 rounded-2xl border border-stone-200/80 dark:border-stone-800 select-none shadow-xs"
              aria-live="polite"
              aria-atomic="true"
            >
              <div className="relative h-7 w-7 overflow-hidden inline-flex items-center justify-center font-extrabold text-xl sm:text-2xl text-stone-950 dark:text-white">
                <AnimatePresence mode="wait" initial={false}>
                  <motion.span
                    key={currentTheme.num}
                    initial={{ y: 14, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -14, opacity: 0 }}
                    transition={{
                      duration: prefersReducedMotion ? 0 : 0.35,
                      ease: [0.16, 1, 0.3, 1],
                    }}
                    className="absolute"
                  >
                    {currentTheme.num}
                  </motion.span>
                </AnimatePresence>
              </div>
              <span className="text-stone-400 dark:text-stone-500 text-sm sm:text-base font-semibold ml-1.5 tracking-wider">
                / 06
              </span>
            </div>
          </motion.div>
        </div>

        {/* ==================================================
            MAIN INTERACTIVE GALLERY: DESKTOP & TABLET
            ================================================== */}
        <div className="hidden md:block">
          <div
            ref={galleryRef}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerEnd}
            onPointerCancel={handlePointerEnd}
            className="relative h-[530px] lg:h-[570px] flex gap-3.5 select-none rounded-[2rem] p-1.5 cursor-grab active:cursor-grabbing transition-transform duration-150"
            style={{
              transform: `translateX(${dragOffset}px)`,
            }}
          >
            {THEMES.map((theme, index) => {
              const isActive = index === activeIdx;
              const Icon = theme.icon;

              return (
                <motion.div
                  key={theme.id}
                  tabIndex={0}
                  role="button"
                  aria-pressed={isActive}
                  aria-label={`${theme.title}, theme ${theme.num} of 06`}
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{
                    duration: 0.6,
                    delay: 0.12 + index * 0.08,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  onMouseEnter={() => {
                    setActiveIdx(index);
                    setHasInteracted(true);
                  }}
                  onMouseMove={(e) => handleMouseMove(e, index)}
                  onMouseLeave={handleMouseLeave}
                  onClick={() => {
                    setActiveIdx(index);
                    setHasInteracted(true);
                  }}
                  onKeyDown={(e) => handleKeyDown(e, index)}
                  className={cn(
                    'group relative h-full rounded-[1.75rem] overflow-hidden cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-amber-400',
                    'transition-all duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] flex flex-col justify-between p-6 lg:p-7',
                    isActive
                      ? 'border border-amber-400/50 dark:border-amber-400/40 shadow-2xl shadow-stone-950/25 ring-1 ring-amber-400/20'
                      : 'border border-stone-200/80 dark:border-white/10 hover:border-stone-400/40 dark:hover:border-white/20'
                  )}
                  style={{
                    // Active card occupies ~42-45%, inactive cards share remaining
                    flex: isActive ? '4.5 1 0%' : '1 1 0%',
                    minWidth: isActive ? '340px' : '72px',
                    transition: prefersReducedMotion
                      ? 'none'
                      : 'flex 700ms cubic-bezier(0.16, 1, 0.3, 1), min-width 700ms cubic-bezier(0.16, 1, 0.3, 1)',
                  }}
                >
                  {/* Background Image: B&W -> Cinematic Color Transition + Parallax */}
                  <div className="absolute inset-0 overflow-hidden bg-stone-900 pointer-events-none">
                    <img
                      src={theme.image}
                      alt={theme.title}
                      loading="lazy"
                      className="absolute inset-0 w-full h-full object-cover will-change-transform"
                      style={{
                        // Inactive: ~80% grayscale (keeps 20% saturation alive as required)
                        // Active: 100% full cinematic color, scale 1.05 + subtle cursor parallax
                        filter: isActive
                          ? 'grayscale(0%) brightness(1.02) contrast(1.05)'
                          : 'grayscale(80%) brightness(0.82) contrast(1.02)',
                        transform:
                          isActive && !prefersReducedMotion
                            ? `scale(1.06) translate3d(${parallax.x}px, ${parallax.y}px, 0)`
                            : 'scale(1) translate3d(0, 0, 0)',
                        transition: isDragging
                          ? 'none'
                          : prefersReducedMotion
                          ? 'none'
                          : 'filter 750ms cubic-bezier(0.16, 1, 0.3, 1), transform 750ms cubic-bezier(0.16, 1, 0.3, 1)',
                      }}
                    />

                    {/* Charcoal Overlays */}
                    <div
                      className={cn(
                        'absolute inset-0 transition-opacity duration-700 ease-out',
                        isActive
                          ? 'bg-gradient-to-t from-stone-950/95 via-stone-950/40 to-stone-950/10'
                          : 'bg-gradient-to-t from-stone-950/90 via-stone-950/60 to-stone-950/30 group-hover:from-stone-950/80'
                      )}
                    />
                  </div>

                  {/* Top Bar: Number & Icon */}
                  <div className="relative z-10 flex items-center justify-between pointer-events-none">
                    <div
                      className={cn(
                        'w-10 h-10 rounded-xl flex items-center justify-center backdrop-blur-md transition-all duration-500',
                        isActive
                          ? 'bg-amber-400 text-stone-950 shadow-md shadow-amber-400/20'
                          : 'bg-black/40 text-stone-300 border border-white/15 group-hover:text-amber-300 group-hover:border-amber-400/30'
                      )}
                    >
                      <Icon className="w-5 h-5" />
                    </div>

                    <span
                      className={cn(
                        'font-mono text-xs font-bold tracking-wider px-2.5 py-1 rounded-full backdrop-blur-md transition-all duration-500',
                        isActive
                          ? 'bg-black/60 text-amber-300 border border-amber-400/30'
                          : 'bg-black/40 text-white/70 border border-white/10'
                      )}
                    >
                      {theme.num}
                    </span>
                  </div>

                  {/* INACTIVE STATE CONTENT (Clean vertical editorial preview) */}
                  {!isActive && (
                    <div className="relative z-10 mt-auto pointer-events-none transition-opacity duration-500 pb-2">
                      <div
                        className="flex items-center gap-3"
                        style={{
                          writingMode: 'vertical-rl',
                          transform: 'rotate(180deg)',
                        }}
                      >
                        <span className="text-xs font-mono font-bold tracking-widest text-amber-400/80">
                          {theme.num}
                        </span>
                        <p className="font-extrabold text-xs lg:text-sm text-white/90 tracking-wider uppercase group-hover:text-amber-300 transition-colors whitespace-nowrap">
                          {theme.title}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* ACTIVE STATE CONTENT: Animated in */}
                  {isActive && (
                    <div className="relative z-10 mt-auto space-y-3 pointer-events-auto">
                      {/* Restrained Yatri Setu Gold Accent Bar */}
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: 44 }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                        className="h-1 bg-amber-400 rounded-full mb-2"
                      />

                      {/* Animated Title: Out opacity 1->0 y 0->-8, In opacity 0->1 y 8->0 */}
                      <div className="overflow-hidden">
                        <AnimatePresence mode="wait">
                          <motion.h3
                            key={`title-${theme.id}`}
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -8 }}
                            transition={{
                              duration: prefersReducedMotion ? 0 : 0.45,
                              ease: [0.16, 1, 0.3, 1],
                            }}
                            className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white tracking-tight drop-shadow-sm"
                          >
                            {theme.title}
                          </motion.h3>
                        </AnimatePresence>
                      </div>

                      {/* Supporting Description */}
                      <motion.p
                        key={`desc-${theme.id}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{
                          duration: prefersReducedMotion ? 0 : 0.5,
                          delay: 0.08,
                          ease: 'easeOut',
                        }}
                        className="text-xs sm:text-sm text-stone-200/90 max-w-md leading-relaxed font-medium"
                      >
                        {theme.desc}
                      </motion.p>

                      {/* Metadata Badges */}
                      <motion.div
                        key={`tags-${theme.id}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{
                          duration: prefersReducedMotion ? 0 : 0.5,
                          delay: 0.15,
                          ease: 'easeOut',
                        }}
                        className="flex flex-wrap gap-2 pt-1"
                      >
                        {theme.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2.5 py-1 rounded-full bg-black/50 backdrop-blur-md border border-amber-400/25 text-[10px] font-mono tracking-wider font-bold text-amber-300 uppercase shadow-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </motion.div>

                      {/* CTA Button */}
                      <motion.div
                        key={`cta-${theme.id}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{
                          duration: prefersReducedMotion ? 0 : 0.5,
                          delay: 0.22,
                          ease: 'easeOut',
                        }}
                        className="pt-2"
                      >
                        <Link
                          href={`/destinations?query=${encodeURIComponent(theme.query)}`}
                          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-amber-400 hover:bg-amber-300 text-stone-950 font-bold text-xs tracking-wider uppercase transition-all duration-300 shadow-lg shadow-amber-500/20 group/btn"
                        >
                          <span>Explore Destinations</span>
                          <ArrowRight className="w-3.5 h-3.5 group-hover/btn:translate-x-1 transition-transform duration-300" />
                        </Link>
                      </motion.div>
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* ==================================================
            MOBILE HORIZONTAL SWIPE GALLERY
            ================================================== */}
        <div className="block md:hidden">
          <div
            ref={mobileScrollRef}
            onScroll={handleMobileScroll}
            className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4 pt-1 px-1 -mx-4 px-4 scrollbar-none"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
          >
            {THEMES.map((theme, index) => {
              const isActive = index === activeIdx;
              const Icon = theme.icon;

              return (
                <div
                  key={theme.id}
                  onClick={() => scrollMobileTo(index)}
                  className={cn(
                    'snap-center shrink-0 w-[82vw] max-w-[340px] h-[460px] rounded-3xl overflow-hidden relative flex flex-col justify-between p-6 transition-all duration-500',
                    isActive
                      ? 'border-2 border-amber-400/60 shadow-xl shadow-stone-950/20'
                      : 'border border-stone-300/80 dark:border-stone-800 opacity-85'
                  )}
                >
                  {/* Image */}
                  <img
                    src={theme.image}
                    alt={theme.title}
                    className="absolute inset-0 w-full h-full object-cover transition-transform duration-700"
                    style={{
                      filter: isActive
                        ? 'grayscale(0%) brightness(1)'
                        : 'grayscale(75%) brightness(0.85)',
                      transform: isActive ? 'scale(1.05)' : 'scale(1)',
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-stone-950/95 via-stone-950/50 to-stone-950/20" />

                  {/* Top Bar */}
                  <div className="relative z-10 flex items-center justify-between">
                    <div
                      className={cn(
                        'w-9 h-9 rounded-xl flex items-center justify-center backdrop-blur-md',
                        isActive
                          ? 'bg-amber-400 text-stone-950'
                          : 'bg-black/40 text-stone-200 border border-white/20'
                      )}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="font-mono text-xs font-bold tracking-wider px-2.5 py-1 rounded-full bg-black/50 backdrop-blur-md border border-white/15 text-amber-300">
                      {theme.num}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="relative z-10 space-y-2.5">
                    {isActive && (
                      <div className="w-10 h-1 bg-amber-400 rounded-full mb-1.5" />
                    )}

                    <h3 className="text-2xl font-extrabold text-white tracking-tight">
                      {theme.title}
                    </h3>

                    <p className="text-xs text-stone-200 line-clamp-2 leading-relaxed">
                      {theme.desc}
                    </p>

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {theme.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 rounded-full bg-black/60 border border-amber-400/30 text-[9px] font-mono font-bold text-amber-300 uppercase"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>

                    <div className="pt-2">
                      <Link
                        href={`/destinations?query=${encodeURIComponent(theme.query)}`}
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-amber-400 text-stone-950 font-bold text-xs tracking-wider uppercase shadow-md"
                      >
                        <span>Explore Destinations</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ==================================================
            FILM STRIP TRACK & INTERACTIVE CONTROLS
            ================================================== */}
        <div className="mt-8 pt-4 flex flex-col sm:flex-row items-center justify-between gap-4 select-none">
          {/* Subtle Drag / Swipe Hint (fades away after first interaction) */}
          <div
            className={cn(
              'text-[11px] font-mono tracking-widest uppercase transition-opacity duration-700 flex items-center gap-2 text-stone-600 dark:text-stone-400 font-medium',
              hasInteracted ? 'opacity-0 pointer-events-none' : 'opacity-100'
            )}
          >
            <MoveHorizontal className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
            <span className="hidden sm:inline">← Drag or hover to explore →</span>
            <span className="sm:hidden">Swipe to explore →</span>
          </div>

          {/* Minimal Editorial Film Strip: 01 ━━━ 02 ━━━ 03 ━━━ 04 ━━━ 05 ━━━ 06 */}
          <div
            className="flex items-center gap-1 sm:gap-2 mx-auto sm:mx-0 font-mono text-xs"
            role="tablist"
            aria-label="Theme selector"
          >
            {THEMES.map((theme, i) => {
              const isActive = i === activeIdx;
              return (
                <React.Fragment key={`track-${theme.id}`}>
                  <button
                    role="tab"
                    aria-selected={isActive}
                    aria-label={`Select theme ${theme.num}: ${theme.title}`}
                    onClick={() => {
                      scrollMobileTo(i);
                      setActiveIdx(i);
                      setHasInteracted(true);
                    }}
                    className={cn(
                      'px-2 py-1 rounded-md transition-all duration-300 cursor-pointer font-bold',
                      isActive
                        ? 'text-amber-700 dark:text-amber-400 scale-110 bg-amber-400/10'
                        : 'text-stone-400 dark:text-stone-600 hover:text-stone-700 dark:hover:text-stone-300'
                    )}
                  >
                    {theme.num}
                  </button>

                  {i < THEMES.length - 1 && (
                    <div className="w-5 sm:w-8 h-[2px] rounded-full bg-stone-200 dark:bg-stone-800 overflow-hidden">
                      <div
                        className={cn(
                          'h-full transition-all duration-500',
                          i < activeIdx
                            ? 'w-full bg-amber-400/60'
                            : i === activeIdx
                            ? 'w-1/2 bg-amber-400'
                            : 'w-0'
                        )}
                      />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
