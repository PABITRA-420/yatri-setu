'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { ChevronLeft, ChevronRight, ArrowRight, Activity, ArrowUpRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { fetchDestinations } from '@/lib/api';

export interface IntelligenceDestination {
  id: string;
  name: string;
  region: string;
  score: number;
  pressureLevel: 'HIGH PRESSURE' | 'MODERATE' | 'CALM' | 'SERENE';
  explanation: string;
  image: string;
  elevation: string;
  footfallTrend: string;
  alternative?: {
    id: string;
    name: string;
    score: number;
    pressureLevel: 'MODERATE' | 'CALM' | 'SERENE';
    matchRate: string;
    explanation: string;
  };
}

const FLOW_DESTINATIONS: IntelligenceDestination[] = [
  {
    id: 'darjeeling',
    name: 'Darjeeling',
    region: 'Eastern Himalayan Ridge • 2,042m',
    score: 88,
    pressureLevel: 'HIGH PRESSURE',
    explanation: 'Holiday congestion peak across Hill Cart Road and the Tiger Hill dawn sunrise corridor.',
    image: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=85',
    elevation: '2,042 m',
    footfallTrend: '+18% vs seasonal baseline',
    alternative: {
      id: 'kalimpong',
      name: 'Kalimpong',
      score: 42,
      pressureLevel: 'MODERATE',
      matchRate: '87% Experience Match',
      explanation: 'Serene orchid ridge with open monasteries, tranquil valleys, and identical Kanchenjunga panoramas.'
    }
  },
  {
    id: 'kalimpong',
    name: 'Kalimpong',
    region: 'Teesta River Ridge • 1,250m',
    score: 42,
    pressureLevel: 'MODERATE',
    explanation: 'Balanced corridor flow with open monastery trails and relaxed local transit.',
    image: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=85',
    elevation: '1,250 m',
    footfallTrend: 'Optimal corridor equilibrium',
    alternative: {
      id: 'lolegaon',
      name: 'Lolegaon',
      score: 18,
      pressureLevel: 'SERENE',
      matchRate: '92% Serenity Match',
      explanation: 'Centuries-old cypress groves and canopy walks with minimal vehicle presence.'
    }
  },
  {
    id: 'lava',
    name: 'Lava',
    region: 'Neora Gateway Pine Ridge • 2,138m',
    score: 24,
    pressureLevel: 'CALM',
    explanation: 'Open pine trails into Neora Valley National Park with serene forest canopy and cool mountain mist.',
    image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=85',
    elevation: '2,138 m',
    footfallTrend: 'Low traffic • Open trails',
    alternative: {
      id: 'rishop',
      name: 'Rishop',
      score: 15,
      pressureLevel: 'SERENE',
      matchRate: '95% Dark Sky Vista',
      explanation: 'High-altitude silent hamlet for 360° unobstructed dawn horizons.'
    }
  },
  {
    id: 'lolegaon',
    name: 'Lolegaon',
    region: 'Kalimpong Foothills • 1,675m',
    score: 18,
    pressureLevel: 'SERENE',
    explanation: 'Historic forest canopy walks and virgin cypress woods experiencing zero transit bottlenecks.',
    image: 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=1200&q=85',
    elevation: '1,675 m',
    footfallTrend: 'Canopy open • Zero queues',
    alternative: {
      id: 'lava',
      name: 'Lava',
      score: 24,
      pressureLevel: 'CALM',
      matchRate: '89% Nature Match',
      explanation: 'Direct forest gateway with verified homestays and birding paths.'
    }
  },
  {
    id: 'rishop',
    name: 'Rishop',
    region: 'Neora Valley High Ridge • 2,591m',
    score: 15,
    pressureLevel: 'SERENE',
    explanation: '360° panoramic Kanchenjunga vantage point with pristine silence, dark skies, and zero crowds.',
    image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=85',
    elevation: '2,591 m',
    footfallTrend: 'Zero vehicle congestion',
    alternative: {
      id: 'kalimpong',
      name: 'Kalimpong',
      score: 42,
      pressureLevel: 'MODERATE',
      matchRate: 'Cultural Hub Transition',
      explanation: 'Easily transition to artisan workshops and heritage colonial cafes down the ridge.'
    }
  },
  {
    id: 'mirik',
    name: 'Mirik',
    region: 'Sumendu Lake Valley • 1,495m',
    score: 38,
    pressureLevel: 'MODERATE',
    explanation: 'Calm lakeside promenade and orange orchard trails with steady, unhurried traveler movement.',
    image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=85',
    elevation: '1,495 m',
    footfallTrend: 'Lakeside relaxed flow',
    alternative: {
      id: 'lava',
      name: 'Lava',
      score: 24,
      pressureLevel: 'CALM',
      matchRate: '90% Forest Sanctuary',
      explanation: 'Deep pine woods for travelers looking for complete solitude away from lake footpaths.'
    }
  }
];

interface LiveFlowIntelligenceProps {
  onOpenCalculator?: () => void;
}

export function LiveFlowIntelligence({ onOpenCalculator }: LiveFlowIntelligenceProps) {
  const [destinations, setDestinations] = useState<IntelligenceDestination[]>(FLOW_DESTINATIONS);
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [displayScore, setDisplayScore] = useState(FLOW_DESTINATIONS[0].score);
  const [touchStartX, setTouchStartX] = useState<number | null>(null);
  const [touchEndX, setTouchEndX] = useState<number | null>(null);
  const autoplayTimerRef = useRef<NodeJS.Timeout | null>(null);

  const activeDestination = destinations[activeIndex] || destinations[0];

  // Fetch real telemetry data on mount to supersede mock fallbacks
  useEffect(() => {
    let isMounted = true;
    async function loadFlowTelemetry() {
      try {
        const liveList = await fetchDestinations();
        if (!isMounted || !liveList || liveList.length === 0) return;

        setDestinations((prev) =>
          prev.map((dest) => {
            const liveMatch = liveList.find((d) => d.id.toLowerCase() === dest.id.toLowerCase());
            let updatedScore = dest.score;
            let updatedPressure = dest.pressureLevel;

            if (liveMatch) {
              updatedScore = liveMatch.crowd_score;
              if (liveMatch.crowd_level === 'VERY HIGH' || liveMatch.crowd_level === 'HIGH') {
                updatedPressure = 'HIGH PRESSURE';
              } else if (liveMatch.crowd_level === 'MEDIUM') {
                updatedPressure = 'MODERATE';
              } else if (liveMatch.crowd_score <= 18) {
                updatedPressure = 'SERENE';
              } else {
                updatedPressure = 'CALM';
              }
            }

            // Also update alternative score if present
            let updatedAlt = dest.alternative;
            if (dest.alternative) {
              const altMatch = liveList.find((d) => d.id.toLowerCase() === dest.alternative?.id.toLowerCase());
              if (altMatch) {
                let altPressure: 'MODERATE' | 'CALM' | 'SERENE' = 'MODERATE';
                if (altMatch.crowd_score <= 18) {
                  altPressure = 'SERENE';
                } else if (altMatch.crowd_score <= 30) {
                  altPressure = 'CALM';
                }
                updatedAlt = {
                  ...dest.alternative,
                  score: altMatch.crowd_score,
                  pressureLevel: altPressure
                };
              }
            }

            return {
              ...dest,
              score: updatedScore,
              pressureLevel: updatedPressure,
              alternative: updatedAlt
            };
          })
        );
      } catch (err) {
        console.warn('LiveFlowIntelligence fetch fallback active:', err);
      }
    }

    loadFlowTelemetry();
    return () => {
      isMounted = false;
    };
  }, []);

  // Animated score counter transition
  useEffect(() => {
    let startTimestamp: number | null = null;
    const duration = 500;
    const startVal = displayScore;
    const targetVal = activeDestination.score;

    if (startVal === targetVal) return;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // Smooth easeOutQuad
      const eased = progress * (2 - progress);
      const current = Math.round(startVal + (targetVal - startVal) * eased);
      setDisplayScore(current);

      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    const animId = window.requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(animId);
  }, [activeIndex, activeDestination.score]);

  // Autoplay cycle every 4.5 seconds
  const nextSlide = useCallback(() => {
    setActiveIndex((prev) => (prev + 1) % destinations.length);
  }, [destinations.length]);

  const prevSlide = useCallback(() => {
    setActiveIndex((prev) => (prev - 1 + destinations.length) % destinations.length);
  }, [destinations.length]);

  useEffect(() => {
    if (isPaused) return;
    autoplayTimerRef.current = setInterval(() => {
      nextSlide();
    }, 4500);

    return () => {
      if (autoplayTimerRef.current) clearInterval(autoplayTimerRef.current);
    };
  }, [isPaused, nextSlide]);

  // Swipe / Drag handling
  const handleTouchStart = (e: React.TouchEvent) => {
    setIsPaused(true);
    setTouchStartX(e.targetTouches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEndX(e.targetTouches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (touchStartX !== null && touchEndX !== null) {
      const distance = touchStartX - touchEndX;
      if (distance > 50) {
        nextSlide();
      } else if (distance < -50) {
        prevSlide();
      }
    }
    setTouchStartX(null);
    setTouchEndX(null);
    setTimeout(() => setIsPaused(false), 2000);
  };

  const getStatusBadge = (level: IntelligenceDestination['pressureLevel']) => {
    switch (level) {
      case 'HIGH PRESSURE':
        return {
          label: 'HIGH PRESSURE',
          textColor: 'text-rose-300',
          dotColor: 'bg-rose-500',
          badgeBg: 'bg-rose-500/10 border-rose-500/30'
        };
      case 'MODERATE':
        return {
          label: 'MODERATE FLOW',
          textColor: 'text-amber-300',
          dotColor: 'bg-amber-500',
          badgeBg: 'bg-amber-500/10 border-amber-500/30'
        };
      case 'CALM':
        return {
          label: 'CALM TRAILS',
          textColor: 'text-emerald-300',
          dotColor: 'bg-emerald-400',
          badgeBg: 'bg-emerald-500/10 border-emerald-500/30'
        };
      case 'SERENE':
      default:
        return {
          label: 'SERENE HAVEN',
          textColor: 'text-emerald-300',
          dotColor: 'bg-emerald-400',
          badgeBg: 'bg-emerald-500/10 border-emerald-500/30'
        };
    }
  };

  const currentBadge = getStatusBadge(activeDestination.pressureLevel);

  return (
    <section
      className="relative w-full py-20 z-10 bg-stone-950 text-white overflow-hidden border-t border-stone-800/60"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Section Editorial Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-stone-800/80">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono font-bold uppercase tracking-widest text-amber-400">
                SECTION 03 • CORE INNOVATION
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-stone-900 border border-stone-700 text-stone-400 text-[11px] font-mono">
                Prototype Intelligence Mode
              </span>
            </div>

            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white">
              LIVE FLOW INTELLIGENCE
            </h2>

            <p className="text-sm sm:text-base text-stone-400 font-light leading-relaxed max-w-xl">
              Where travellers are going. <br className="hidden sm:inline" />
              Where pressure is building. <br className="hidden sm:inline" />
              Where they could go instead.
            </p>
          </div>

          {/* Carousel Manual Controls & Autoplay State */}
          <div className="flex items-center gap-4 self-start md:self-end">
            <div className="text-xs font-mono text-stone-500 hidden sm:block">
              <span className="text-white font-bold">{String(activeIndex + 1).padStart(2, '0')}</span>
              <span className="mx-1">/</span>
              <span>{String(destinations.length).padStart(2, '0')}</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={prevSlide}
                aria-label="Previous destination"
                className="p-3 rounded-xl bg-stone-900/90 hover:bg-stone-800 text-stone-300 hover:text-white border border-stone-800 hover:border-stone-700 transition-all cursor-pointer shadow-sm active:scale-95"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={nextSlide}
                aria-label="Next destination"
                className="p-3 rounded-xl bg-stone-900/90 hover:bg-stone-800 text-stone-300 hover:text-white border border-stone-800 hover:border-stone-700 transition-all cursor-pointer shadow-sm active:scale-95"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Hero Interactive Destination Intelligence Showcase */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          {/* Main Active Card (Center / Left Showcase) */}
          <div className="lg:col-span-8 relative rounded-3xl overflow-hidden bg-stone-900/90 border border-stone-800 shadow-2xl flex flex-col justify-between min-h-[460px] sm:min-h-[520px] transition-all duration-500">
            {/* Background Image with Gentle Zoom & Gradient Overlays */}
            <div className="absolute inset-0 z-0">
              <img
                src={activeDestination.image}
                alt={activeDestination.name}
                key={activeDestination.id}
                className="w-full h-full object-cover object-center animate-in fade-in zoom-in-105 duration-700 filter brightness-[0.75]"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/60 to-transparent" />
              <div className="absolute inset-0 bg-gradient-to-r from-stone-950/90 via-stone-950/40 to-transparent" />
            </div>

            {/* Top Bar inside Active Card */}
            <div className="relative z-10 p-6 sm:p-8 flex items-start justify-between gap-4 flex-wrap">
              <div className="space-y-1">
                <span className="text-xs font-mono text-stone-400 block tracking-wider uppercase">
                  {activeDestination.region}
                </span>
                <h3
                  key={activeDestination.name}
                  className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight animate-in fade-in slide-in-from-left-2 duration-300"
                >
                  {activeDestination.name}
                </h3>
              </div>

              {/* Dynamic Score Counter & Status Badge */}
              <div className="flex flex-col items-end gap-2">
                <div className="px-3.5 py-1.5 rounded-2xl bg-black/60 backdrop-blur-md border border-white/10 shadow-lg text-right">
                  <div className="text-3xl sm:text-4xl font-black font-mono tracking-tight text-white flex items-baseline justify-end gap-1">
                    <span>{displayScore}</span>
                    <span className="text-xs font-mono text-stone-400 font-normal">/ 100</span>
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-stone-400 block">
                    Telemetry Index
                  </span>
                </div>

                <div
                  key={currentBadge.label}
                  className={cn(
                    'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold border backdrop-blur-md animate-in fade-in duration-300',
                    currentBadge.badgeBg,
                    currentBadge.textColor
                  )}
                >
                  <span className={cn('w-2 h-2 rounded-full animate-pulse', currentBadge.dotColor)} />
                  <span>{currentBadge.label}</span>
                </div>
              </div>
            </div>

            {/* Bottom Content inside Active Card */}
            <div className="relative z-10 p-6 sm:p-8 space-y-6 pt-12">
              {/* Short Explanation */}
              <p
                key={activeDestination.explanation}
                className="text-base sm:text-lg text-stone-200 font-normal leading-relaxed max-w-2xl animate-in fade-in duration-400 drop-shadow-sm"
              >
                "{activeDestination.explanation}"
              </p>

              {/* Alternative Intelligence Card or Calmer Flow Callout */}
              {activeDestination.alternative ? (
                <div
                  key={activeDestination.alternative.id}
                  className="p-4 sm:p-5 rounded-2xl bg-black/75 backdrop-blur-xl border border-white/15 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-in fade-in slide-in-from-bottom-2 duration-400"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400 font-bold">
                        RECOMMENDED ALTERNATIVE
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-white/10 text-[10px] font-mono text-stone-300">
                        {activeDestination.alternative.matchRate}
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <h4 className="text-lg font-extrabold text-white">
                        {activeDestination.alternative.name}
                      </h4>
                      <span className="text-xs font-mono text-emerald-400 font-bold">
                        {activeDestination.alternative.score}/100 Crowd Score
                      </span>
                    </div>
                    <p className="text-xs text-stone-300 leading-normal max-w-xl">
                      {activeDestination.alternative.explanation}
                    </p>
                  </div>

                  <Link
                    href={`/destinations/${activeDestination.alternative.id}`}
                    className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-stone-950 font-bold text-xs shrink-0 shadow-md shadow-amber-500/20 transition-all cursor-pointer group"
                  >
                    <span>Find a calmer route</span>
                    <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                  </Link>
                </div>
              ) : (
                <div className="p-4 rounded-2xl bg-black/60 backdrop-blur-md border border-white/10 flex items-center justify-between gap-4">
                  <span className="text-xs text-stone-300 font-mono">
                    This corridor is operating at peak tranquility. Verified Panchayat stays open.
                  </span>
                  <Link
                    href={`/destinations/${activeDestination.id}`}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 hover:underline shrink-0"
                  >
                    <span>Explore {activeDestination.name}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Corridor Destinations Peek & Selector Rail */}
          <div className="lg:col-span-4 flex flex-col justify-between space-y-4">
            <div className="flex items-center justify-between pb-1">
              <span className="text-xs font-mono uppercase tracking-wider text-stone-400">
                Himalayan Circuit Nodes
              </span>
              <span className="text-xs text-stone-500 font-mono">
                Click to inspect
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3 overflow-hidden">
              {destinations.map((dest, idx) => {
                const isActive = idx === activeIndex;
                const badge = getStatusBadge(dest.pressureLevel);

                return (
                  <button
                    key={dest.id}
                    type="button"
                    onClick={() => {
                      setActiveIndex(idx);
                      setIsPaused(true);
                      setTimeout(() => setIsPaused(false), 5000);
                    }}
                    className={cn(
                      'group w-full p-3.5 rounded-2xl border text-left transition-all duration-300 flex items-center gap-3.5 cursor-pointer',
                      isActive
                        ? 'bg-stone-900 border-amber-400/50 shadow-lg shadow-black/40 ring-1 ring-amber-400/20'
                        : 'bg-stone-900/40 hover:bg-stone-900/70 border-stone-800/80 hover:border-stone-700 text-stone-400'
                    )}
                  >
                    {/* Small Thumbnail */}
                    <div className="relative w-14 h-14 rounded-xl overflow-hidden shrink-0 bg-stone-800">
                      <img
                        src={dest.image}
                        alt={dest.name}
                        className={cn(
                          'w-full h-full object-cover transition-transform duration-500',
                          isActive ? 'scale-110' : 'group-hover:scale-105 filter brightness-75'
                        )}
                      />
                    </div>

                    {/* Node Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-1">
                        <span
                          className={cn(
                            'text-sm font-extrabold truncate',
                            isActive ? 'text-white' : 'text-stone-300 group-hover:text-white'
                          )}
                        >
                          {dest.name}
                        </span>
                        <span
                          className={cn(
                            'text-xs font-mono font-bold shrink-0',
                            dest.score > 70
                              ? 'text-rose-400'
                              : dest.score > 35
                              ? 'text-amber-400'
                              : 'text-emerald-400'
                          )}
                        >
                          {dest.score}/100
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-[11px] font-mono mt-1">
                        <span className="text-stone-400 truncate">{dest.elevation}</span>
                        <span className={cn('text-[10px] font-bold uppercase', badge.textColor)}>
                          {dest.pressureLevel.replace(' PRESSURE', '')}
                        </span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Quick Link to Itinerary or Alternatives */}
            <div className="pt-2">
              <Link
                href="/destinations"
                className="w-full py-3 px-4 rounded-xl bg-stone-900/80 hover:bg-stone-800 border border-stone-800 hover:border-stone-700 text-stone-300 hover:text-white text-xs font-medium flex items-center justify-between transition-colors group"
              >
                <span>Browse all 18 Himalayan Circuit Stays</span>
                <ArrowUpRight className="w-3.5 h-3.5 text-stone-500 group-hover:text-amber-400 transition-colors" />
              </Link>
            </div>
          </div>
        </div>

        {/* Section Bottom Footer with Transparent Explanation Trigger */}
        <div className="pt-6 border-t border-stone-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-stone-400 font-mono">
          <div className="flex items-center gap-2 text-stone-400">
            <Activity className="w-3.5 h-3.5 text-amber-400" />
            <span>Telemetry calibrated via deterministic 6-factor pressure baseline.</span>
          </div>

          {onOpenCalculator ? (
            <button
              type="button"
              onClick={onOpenCalculator}
              className="inline-flex items-center gap-1 font-bold text-amber-400 hover:text-amber-300 hover:underline transition-colors cursor-pointer"
            >
              <span>How is this calculated? →</span>
            </button>
          ) : (
            <Link
              href="/admin/command-center"
              className="inline-flex items-center gap-1 font-bold text-amber-400 hover:text-amber-300 hover:underline transition-colors cursor-pointer"
            >
              <span>How is this calculated? →</span>
            </Link>
          )}
        </div>
      </div>
    </section>
  );
}
