'use client';

import React, { useState, useEffect, useRef } from 'react';

export function ScrollProgress() {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const [hoverPercent, setHoverPercent] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (totalHeight <= 0) {
        setScrollProgress(0);
        return;
      }
      const currentScroll = window.scrollY;
      const progress = (currentScroll / totalHeight) * 100;
      setScrollProgress(Math.min(100, Math.max(0, progress)));
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleTrackClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = Math.max(0, Math.min(1, clickX / rect.width));
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    const targetY = ratio * totalHeight;
    window.scrollTo({ top: targetY, behavior: 'smooth' });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = Math.max(0, Math.min(1, clickX / rect.width));
    setHoverPercent(Math.round(ratio * 100));
  };

  return (
    <div
      ref={containerRef}
      onClick={handleTrackClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setHoverPercent(null);
      }}
      className="fixed top-0 left-0 right-0 z-50 h-1.5 sm:h-2 bg-stone-950/40 backdrop-blur-md cursor-pointer group transition-all duration-300"
      title="Click to jump scroll"
      role="progressbar"
      aria-valuenow={Math.round(scrollProgress)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      {/* Background Track Glow */}
      <div className="absolute inset-0 bg-stone-900/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      {/* Progress Bar Fill */}
      <div
        className="h-full bg-gradient-to-r from-amber-500 via-emerald-400 to-amber-300 transition-all duration-75 ease-out shadow-[0_0_12px_rgba(245,158,11,0.8)] relative"
        style={{ width: `${scrollProgress}%` }}
      >
        {/* Leading Glowing Bead / Particle */}
        {scrollProgress > 0 && (
          <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 w-3.5 h-3.5 rounded-full bg-amber-200 border-2 border-amber-500 shadow-[0_0_15px_#f59e0b] animate-pulse pointer-events-none" />
        )}
      </div>

      {/* Hover Percentage Tooltip */}
      {isHovered && hoverPercent !== null && (
        <div
          className="absolute top-3 px-2 py-0.5 rounded-full bg-stone-900 border border-amber-500/50 text-[10px] font-extrabold text-amber-300 shadow-xl backdrop-blur-md pointer-events-none -translate-x-1/2 animate-in fade-in zoom-in-95 duration-100"
          style={{ left: `${hoverPercent}%` }}
        >
          Jump to {hoverPercent}%
        </div>
      )}
    </div>
  );
}
