'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowUpRight, Shield, HeartHandshake, PhoneCall } from 'lucide-react';
import { motion, useInView } from 'motion/react';
import { cn } from '@/lib/utils';

export const Footer: React.FC = () => {
  const [hoveredNav, setHoveredNav] = useState<'explore' | 'plan' | 'mytrip' | null>(null);
  const [isReducedMotion, setIsReducedMotion] = useState(false);
  
  const footerRef = useRef<HTMLElement>(null);
  const isInView = useInView(footerRef, { once: true, amount: 0.15 });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
      setIsReducedMotion(mq.matches);
      const handler = (e: MediaQueryListEvent) => setIsReducedMotion(e.matches);
      mq.addEventListener('change', handler);
      return () => mq.removeEventListener('change', handler);
    }
  }, []);

  return (
    <footer
      ref={footerRef}
      className="relative w-full bg-[#080B10] text-stone-100 border-t border-white/10 overflow-hidden select-none"
      aria-label="Site Footer — The Journey Continues"
    >
      {/* Subtle Himalayan ambient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-32 bg-[radial-gradient(ellipse_60%_50%_at_50%_0%,rgba(245,158,11,0.12),transparent)] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(#ffffff_0.5px,transparent_0.5px)] opacity-[0.015] pointer-events-none" />

      <div className="max-w-[1440px] mx-auto px-4 sm:px-8 lg:px-12 py-8 sm:py-10 relative z-10 space-y-6">
        
        {/* TOP ROW: ICONIC BRAND LOGO LOCKUP (LEFT) · TOPOGRAPHIC ROUTE (CENTER) · NAV (RIGHT) */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-6 border-b border-white/10">
          
          {/* Brand Logo & Editorial Emblem Showcase */}
          <Link href="/" className="flex items-center gap-4 group/logo shrink-0 cursor-pointer">
            {/* Luminous Illuminated Logo Emblem */}
            <div className="relative">
              {/* Multi-tier Amber Ambient Radiant Halo */}
              <div className="absolute -inset-2 bg-gradient-to-r from-amber-500/35 via-amber-400/25 to-amber-600/20 rounded-3xl blur-xl opacity-70 group-hover/logo:opacity-100 transition-all duration-700" />
              <div className="absolute -inset-0.5 bg-amber-400/30 rounded-2xl blur-sm opacity-50 group-hover/logo:opacity-90 transition-all duration-500" />
              
              {/* Sculpted Glassmorphic Emblem Frame with Dual Metallic Amber Ring */}
              <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-stone-850 via-stone-900 to-[#0c0f17] border-2 border-amber-400/60 p-2 sm:p-2.5 shadow-[0_0_25px_rgba(245,158,11,0.25)] ring-1 ring-white/20 flex items-center justify-center transition-all duration-500 group-hover/logo:scale-105 group-hover/logo:border-amber-300 group-hover/logo:shadow-[0_0_35px_rgba(245,158,11,0.45)]">
                <Image
                  src="/logo-emblem.png"
                  alt="Yatri Setu Logo"
                  width={56}
                  height={56}
                  className="w-full h-full object-contain filter drop-shadow-[0_2px_10px_rgba(245,158,11,0.4)]"
                  priority
                />
              </div>
            </div>

            {/* Brand Typography, Bilingual Devanagari Jewel & Telemetry Badges */}
            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-2.5">
                <span className="font-black text-2xl sm:text-3xl tracking-tight text-white block leading-none transition-colors group-hover/logo:text-amber-200">
                  Yatri<span className="font-editorial italic font-normal text-amber-400 ml-1 drop-shadow-[0_0_12px_rgba(245,158,11,0.45)]">Setu</span>
                </span>
                <span className="text-[10px] sm:text-[11px] font-bold text-amber-200 font-sans px-2.5 py-0.5 rounded-full bg-gradient-to-r from-amber-500/20 via-amber-400/30 to-amber-500/20 border border-amber-400/50 shadow-xs tracking-wide">
                  यात्री सेतु
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-2 mt-1.5 text-[10px] sm:text-[11px] font-mono tracking-wider text-stone-400">
                <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  LIVE
                </span>
                <span className="text-stone-600 hidden sm:inline">•</span>
                <span className="text-stone-300 font-medium uppercase tracking-widest">
                  Himalayan Flow Intelligence
                </span>
                <span className="text-stone-600 hidden md:inline">•</span>
                <span className="text-amber-400/90 font-bold hidden md:inline">
                  SIH 2026
                </span>
              </div>
            </div>
          </Link>

          {/* Center: Interactive Himalayan Topographic Route Line */}
          <div className="flex-1 max-w-xs sm:max-w-sm hidden sm:flex flex-col items-center">
            <div className="w-full h-9 relative flex items-center justify-center">
              <svg
                viewBox="0 0 400 40"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-full h-full overflow-visible"
                preserveAspectRatio="xMidYMid meet"
                aria-hidden="true"
              >
                <path
                  d="M 0 30 L 50 30 L 90 18 L 130 30 L 190 30 L 230 10 L 270 30 L 320 30 L 360 18 L 400 30"
                  stroke="rgba(255, 255, 255, 0.22)"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M 10 30 C 60 30, 90 20, 130 25 C 170 30, 200 12, 230 14 C 270 16, 300 28, 340 20 C 370 14, 385 28, 395 30"
                  stroke={
                    hoveredNav === 'plan'
                      ? '#34D399'
                      : hoveredNav === 'explore' || hoveredNav === 'mytrip'
                      ? '#F59E0B'
                      : 'rgba(245, 158, 11, 0.85)'
                  }
                  strokeWidth={hoveredNav ? '2.5' : '2'}
                  strokeDasharray={hoveredNav === 'plan' ? '5 3' : 'none'}
                  strokeLinecap="round"
                  className="transition-all duration-300 ease-out filter drop-shadow-[0_0_8px_rgba(245,158,11,0.4)]"
                />
                <circle
                  cx="230"
                  cy="12"
                  r={hoveredNav ? '4.5' : '3.5'}
                  fill={hoveredNav ? '#F59E0B' : '#FBBF24'}
                  className="transition-all duration-300 filter drop-shadow-[0_0_6px_rgba(245,158,11,0.8)]"
                />
              </svg>
            </div>
            <span className="text-[9px] font-mono tracking-widest uppercase text-stone-400 font-semibold">
              {hoveredNav === 'explore'
                ? 'SISTER SANCTUARIES ACTIVE'
                : hoveredNav === 'plan'
                ? 'CROWD-OPTIMIZED FLOW READY'
                : hoveredNav === 'mytrip'
                ? 'YATRI MITRA 112 MESH CONNECTED'
                : 'ACTIVE HIMALAYAN PASSES'}
            </span>
          </div>

          {/* Right: Minimal Navigation Links */}
          <nav className="flex items-center gap-5 sm:gap-6 text-xs font-mono tracking-wider uppercase" aria-label="Footer Navigation">
            <Link
              href="/destinations"
              onMouseEnter={() => setHoveredNav('explore')}
              onMouseLeave={() => setHoveredNav(null)}
              className={cn(
                'inline-flex items-center gap-1 transition-colors duration-200 py-1 cursor-pointer font-bold',
                hoveredNav === 'explore' ? 'text-amber-400' : 'text-stone-400 hover:text-stone-200'
              )}
            >
              <span>Explore</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-stone-500 group-hover:text-amber-400" />
            </Link>

            <Link
              href="/itinerary"
              onMouseEnter={() => setHoveredNav('plan')}
              onMouseLeave={() => setHoveredNav(null)}
              className={cn(
                'inline-flex items-center gap-1 transition-colors duration-200 py-1 cursor-pointer font-bold',
                hoveredNav === 'plan' ? 'text-amber-400' : 'text-stone-400 hover:text-stone-200'
              )}
            >
              <span>Plan</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-stone-500 group-hover:text-amber-400" />
            </Link>

            <Link
              href="/safety/sos"
              onMouseEnter={() => setHoveredNav('mytrip')}
              onMouseLeave={() => setHoveredNav(null)}
              className={cn(
                'inline-flex items-center gap-1 transition-colors duration-200 py-1 cursor-pointer font-bold',
                hoveredNav === 'mytrip' ? 'text-amber-400' : 'text-stone-400 hover:text-stone-200'
              )}
            >
              <span>My Trip</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-stone-500 group-hover:text-amber-400" />
            </Link>
          </nav>

        </div>

        {/* BOTTOM ROW: COPYRIGHT (LEFT) & HELPLINE/SOCIAL LINKS (RIGHT) */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-stone-400">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 text-center sm:text-left text-[11px]">
            <span className="font-bold text-stone-300">Yatri Setu</span>
            <span className="text-stone-700">•</span>
            <span>© 2026 Smart India Hackathon</span>
            <span className="text-stone-700 hidden sm:inline">•</span>
            <span className="text-stone-400">Active Decongestion & Traveler Safety</span>
          </div>

          <div className="flex items-center gap-5 text-[11px] text-stone-400">
            <a
              href="https://instagram.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-amber-400 transition-colors duration-200"
            >
              Instagram
            </a>
            <span className="text-stone-800">•</span>
            <a
              href="https://github.com/kusalar/yatri-setu"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-amber-400 transition-colors duration-200"
            >
              GitHub
            </a>
            <span className="text-stone-800">•</span>
            <Link
              href="/safety/sos"
              className="hover:text-rose-400 text-rose-400/90 transition-colors duration-200 font-bold inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/25"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping" />
              <span>SOS 112 Ready</span>
            </Link>
          </div>
        </div>

      </div>
    </footer>
  );
};
