'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  ChevronDown,
  Compass,
  Flame,
  Sparkles,
  Home,
  Calendar,
  Navigation,
  Shield,
  Landmark,
  Activity,
  Ticket,
  MapPin,
  ArrowRight,
  Menu,
  X,
  ShieldAlert,
  Layers,
  FileCheck,
  CloudSun,
  UserCheck
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/animate-ui/components/buttons/button';
import { RadioTower } from '@/components/animate-ui/icons/radio-tower';

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const closeTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close dropdown on route change
  useEffect(() => {
    setOpenDropdown(null);
    setMobileMenuOpen(false);
  }, [pathname]);

  const handleMouseEnter = (menuKey: string) => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
    setOpenDropdown(menuKey);
  };

  const handleMouseLeave = () => {
    closeTimeoutRef.current = setTimeout(() => {
      setOpenDropdown(null);
    }, 220);
  };

  const toggleDropdown = (menuKey: string) => {
    setOpenDropdown(prev => (prev === menuKey ? null : menuKey));
  };

  // Structured menu items with rich descriptions & status badges
  const exploreMenu = {
    title: 'Destination Intelligence',
    tag: 'Flow Telemetry',
    items: [
      {
        title: 'Destination Overview',
        desc: 'Curated Himalayan catalog with multi-factor footfall ratings',
        href: '/destinations',
        icon: Compass,
        badge: 'Catalog'
      },
      {
        title: 'Crowd Intelligence',
        desc: 'Real-time footfall density, bottleneck telemetry & choke points',
        href: '/destinations/darjeeling/crowd',
        icon: Flame,
        badge: 'Live 88/100',
        badgeColor: 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20'
      },
      {
        title: 'Alternative Sanctuaries',
        desc: 'Similarity & capacity-aware advisor unburdening fragile ridges',
        href: '/destinations/darjeeling/alternatives',
        icon: Sparkles,
        badge: '87% Match',
        badgeColor: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20'
      },
      {
        title: 'Rural Homestays',
        desc: 'Verified panchayat-certified cottages where 90% stays with hosts',
        href: '/homestays',
        icon: Home,
        badge: 'Panchayat',
        badgeColor: 'bg-amber-500/10 text-amber-800 dark:text-amber-400 border-amber-500/20'
      }
    ],
    footer: {
      title: 'Digital Travel Pass & Route Allocation',
      desc: 'Seamless booking confirmation, pass issuance & gate permits',
      href: '/dashboard',
      actionText: 'View Digital Pass'
    }
  };

  const planMenu = {
    title: 'Trip Planning & Optimization',
    tag: 'Adaptive Engine',
    items: [
      {
        title: 'AI Adaptive Itinerary',
        desc: '3-day crowd-avoiding schedules balancing key sights & hidden hamlets',
        href: '/itinerary',
        icon: Calendar,
        badge: 'AI Smart',
        badgeColor: 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border-indigo-500/20'
      },
      {
        title: 'Alternative Route Advisor',
        desc: 'Choose serene places with high climatic and cultural similarity',
        href: '/destinations/darjeeling/alternatives',
        icon: MapPin,
        badge: 'Smart Switch',
        badgeColor: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20'
      },
      {
        title: 'Capacity & Chokepoint Alerts',
        desc: 'Predictive crowd forecasting to time ridge entries and vehicle transit',
        href: '/destinations/darjeeling/crowd',
        icon: Layers,
        badge: 'Predictive',
        badgeColor: 'bg-amber-500/10 text-amber-800 dark:text-amber-400 border-amber-500/20'
      }
    ]
  };

  const myTripMenu = {
    title: 'Traveler Companion & Services',
    tag: 'Live Journey',
    items: [
      {
        title: 'Trip Companion',
        desc: 'Active voyage manager, offline itinerary & dynamic checkpoint advisories',
        href: '/trips',
        icon: Navigation,
        badge: 'Active Trip',
        badgeColor: 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20'
      },
      {
        title: 'Digital Pass & Green Credits™',
        desc: 'QR gate permits, verification stamps & earned sustainability credits',
        href: '/dashboard',
        icon: Ticket,
        badge: 'Wallet',
        badgeColor: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20'
      },
      {
        title: 'Verified Stay Bookings',
        desc: 'Sherpa & local homestay reservations with village development fund',
        href: '/homestays',
        icon: Home,
        badge: 'Stays',
        badgeColor: 'bg-amber-500/10 text-amber-800 dark:text-amber-400 border-amber-500/20'
      },
      {
        title: 'Mountain Weather & Safety',
        desc: 'Live high-altitude forecasts, trail alerts & 24/7 safety network',
        href: '/safety',
        icon: CloudSun,
        badge: 'Safety',
        badgeColor: 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20'
      }
    ]
  };

  const moreMenu = {
    title: 'Portals & Regional Governance',
    tag: 'Ecosystem',
    items: [
      {
        title: 'Host Portal',
        desc: 'Rural homestay host registration, inventory and revenue telemetry',
        href: '/host',
        icon: UserCheck,
        badge: 'Hosts'
      },
      {
        title: 'Gram Panchayat',
        desc: 'Local body eco-audit, carry-capacity quotas & permit verifications',
        href: '/panchayat',
        icon: Landmark,
        badge: 'Governance'
      },
      {
        title: 'Ops Command Center',
        desc: 'District administrative overview, real-time footfall alerts & SOS triage',
        href: '/admin/command-center',
        icon: Activity,
        badge: 'Admin Telemetry'
      }
    ]
  };

  return (
    <>
      <header
        className={cn(
          'sticky top-0 z-50 transition-all duration-300',
          scrolled
            ? 'bg-[#FAF8F5]/95 dark:bg-[#0E131E]/95 backdrop-blur-xl border-b border-stone-300/80 dark:border-stone-800/80 shadow-[0_4px_20px_rgba(0,0,0,0.04)] dark:shadow-[0_4px_25px_rgba(0,0,0,0.4)]'
            : 'bg-[#F6F4F0] dark:bg-[#0C0F14] border-b border-stone-200/80 dark:border-stone-800/50'
        )}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-[72px]">

            {/* 1. Left: Brand Logo Lockup (Increased Logo & Crisp Prominence) */}
            <Link href="/" className="flex items-center gap-3.5 group shrink-0">
              <div className="w-[52px] h-[52px] rounded-2xl overflow-hidden shadow-sm transition-transform duration-300 group-hover:scale-105 border border-stone-300/80 dark:border-stone-700/80 bg-white dark:bg-stone-900 flex items-center justify-center p-1 ring-1 ring-stone-900/5 dark:ring-white/10">
                <Image
                  src="/logo.png"
                  alt="Yatri Setu Logo"
                  width={52}
                  height={52}
                  className="w-full h-full object-contain"
                  priority
                />
              </div>
              <div className="flex flex-col justify-center">
                <span className="font-black text-[25px] sm:text-[27px] tracking-tight leading-none text-stone-950 dark:text-white group-hover:text-amber-700 dark:group-hover:text-amber-400 transition-colors">
                  Yatri<span className="font-editorial italic font-normal text-amber-700 dark:text-amber-400 ml-1">Setu</span>
                </span>
                <span className="text-[11px] sm:text-xs text-stone-600 dark:text-stone-400 tracking-wider font-semibold mt-0.5 hidden sm:block">
                  Himalayan Flow Intelligence
                </span>
              </div>
            </Link>

            {/* 2. Center: Explore | Plan | My Trip (Slimmer Pill Height & Bolder Legible Typography) */}
            <nav className="hidden lg:flex items-center gap-1.5 bg-[#EDE9E2]/85 dark:bg-stone-900/90 p-1 sm:p-1.5 rounded-full border border-stone-300/90 dark:border-stone-700/80 shadow-xs backdrop-blur-md">

              {/* EXPLORE DROPDOWN */}
              <div
                className="relative"
                onMouseEnter={() => handleMouseEnter('explore')}
                onMouseLeave={handleMouseLeave}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown('explore')}
                  className={cn(
                    'flex items-center gap-2 px-3.5 py-1.5 rounded-full text-[14px] font-bold tracking-tight transition-all duration-200 cursor-pointer',
                    openDropdown === 'explore' || pathname.startsWith('/destinations') || pathname.startsWith('/homestays')
                      ? 'bg-white dark:bg-stone-800 text-stone-950 dark:text-white shadow-xs border border-stone-200/90 dark:border-stone-700'
                      : 'text-stone-750 hover:text-stone-950 dark:text-stone-200 dark:hover:text-white hover:bg-white/60 dark:hover:bg-stone-800/60'
                  )}
                >
                  <Compass className="w-4 h-4 text-amber-750 dark:text-amber-400" />
                  <span>Explore</span>
                  <ChevronDown className={cn('w-3.5 h-3.5 transition-transform duration-200 text-stone-400', openDropdown === 'explore' && 'rotate-180 text-amber-700 dark:text-amber-400')} />
                </button>

                {openDropdown === 'explore' && (
                  <div className="absolute top-full left-0 mt-3 w-[27rem] rounded-2xl bg-[#FCFAF7]/98 dark:bg-[#111622]/98 backdrop-blur-2xl border border-stone-300/90 dark:border-stone-700/80 shadow-[0_24px_50px_-12px_rgba(28,25,23,0.18)] dark:shadow-[0_24px_60px_-12px_rgba(0,0,0,0.7)] p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-200 ring-1 ring-black/5 dark:ring-white/10">
                    <div className="px-3 py-2 text-xs font-extrabold uppercase tracking-wider text-amber-950 dark:text-amber-300 border-b border-stone-200/80 dark:border-stone-800 mb-2.5 flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-amber-600"></span>
                        {exploreMenu.title}
                      </span>
                      <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-900 dark:text-amber-300 font-mono font-bold">
                        {exploreMenu.tag}
                      </span>
                    </div>

                    <div className="space-y-2">
                      {exploreMenu.items.map((item) => {
                        const Icon = item.icon;
                        const isCurrent = pathname === item.href;
                        return (
                          <Link
                            key={item.title}
                            href={item.href}
                            className={cn(
                              'group flex items-start gap-3.5 p-3 rounded-xl border transition-all duration-150',
                              isCurrent
                                ? 'bg-amber-500/15 text-amber-950 dark:text-amber-100 border-amber-500/40 shadow-xs'
                                : 'bg-transparent hover:bg-white dark:hover:bg-stone-800/80 border-transparent hover:border-stone-200/90 dark:hover:border-stone-700 hover:shadow-xs text-stone-900 dark:text-stone-100'
                            )}
                          >
                            <div className="w-10 h-10 rounded-xl bg-amber-500/15 dark:bg-amber-400/15 text-amber-800 dark:text-amber-300 border border-amber-500/25 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                              <Icon className="w-5 h-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-[15px] font-bold text-stone-950 dark:text-white group-hover:text-amber-800 dark:group-hover:text-amber-300 transition-colors">
                                  {item.title}
                                </span>
                                <span className={cn(
                                  'text-xs px-2.5 py-0.5 rounded-md font-mono font-bold border shrink-0',
                                  item.badgeColor || 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 border-stone-200 dark:border-stone-700'
                                )}>
                                  {item.badge}
                                </span>
                              </div>
                              <p className="text-xs sm:text-[13px] text-stone-600 dark:text-stone-300 line-clamp-1 mt-1 leading-normal font-medium">
                                {item.desc}
                              </p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>

                    {/* Booking & Pass Flow Link */}
                    <div className="mt-3 pt-3 border-t border-stone-200/80 dark:border-stone-800 px-3 pb-1">
                      <Link
                        href={exploreMenu.footer.href}
                        className="flex items-center justify-between text-[13px] font-bold text-amber-900 dark:text-amber-400 hover:text-amber-950 dark:hover:text-white transition-colors py-1 group"
                      >
                        <div className="flex items-center gap-2">
                          <FileCheck className="w-4 h-4 text-amber-700 dark:text-amber-400" />
                          <span>{exploreMenu.footer.title}</span>
                        </div>
                        <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                      </Link>
                    </div>
                  </div>
                )}
              </div>

              {/* PLAN DROPDOWN */}
              <div
                className="relative"
                onMouseEnter={() => handleMouseEnter('plan')}
                onMouseLeave={handleMouseLeave}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown('plan')}
                  className={cn(
                    'flex items-center gap-2 px-3.5 py-1.5 rounded-full text-[14px] font-bold tracking-tight transition-all duration-200 cursor-pointer',
                    openDropdown === 'plan' || pathname === '/itinerary'
                      ? 'bg-white dark:bg-stone-800 text-stone-950 dark:text-white shadow-xs border border-stone-200/90 dark:border-stone-700'
                      : 'text-stone-750 hover:text-stone-950 dark:text-stone-200 dark:hover:text-white hover:bg-white/60 dark:hover:bg-stone-800/60'
                  )}
                >
                  <Calendar className="w-4 h-4 text-amber-750 dark:text-amber-400" />
                  <span>Plan</span>
                  <ChevronDown className={cn('w-3.5 h-3.5 transition-transform duration-200 text-stone-400', openDropdown === 'plan' && 'rotate-180 text-amber-700 dark:text-amber-400')} />
                </button>

                {openDropdown === 'plan' && (
                  <div className="absolute top-full left-0 mt-3 w-[26rem] rounded-2xl bg-[#FCFAF7]/98 dark:bg-[#111622]/98 backdrop-blur-2xl border border-stone-300/90 dark:border-stone-700/80 shadow-[0_24px_50px_-12px_rgba(28,25,23,0.18)] dark:shadow-[0_24px_60px_-12px_rgba(0,0,0,0.7)] p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-200 ring-1 ring-black/5 dark:ring-white/10">
                    <div className="px-3 py-2 text-xs font-extrabold uppercase tracking-wider text-amber-950 dark:text-amber-300 border-b border-stone-200/80 dark:border-stone-800 mb-2.5 flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
                        {planMenu.title}
                      </span>
                      <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-900 dark:text-emerald-300 font-mono font-bold">
                        {planMenu.tag}
                      </span>
                    </div>

                    <div className="space-y-2">
                      {planMenu.items.map((item) => {
                        const Icon = item.icon;
                        const isCurrent = pathname === item.href;
                        return (
                          <Link
                            key={item.title}
                            href={item.href}
                            className={cn(
                              'group flex items-start gap-3.5 p-3 rounded-xl border transition-all duration-150',
                              isCurrent
                                ? 'bg-amber-500/15 text-amber-950 dark:text-amber-100 border-amber-500/40 shadow-xs'
                                : 'bg-transparent hover:bg-white dark:hover:bg-stone-800/80 border-transparent hover:border-stone-200/90 dark:hover:border-stone-700 hover:shadow-xs text-stone-900 dark:text-stone-100'
                            )}
                          >
                            <div className="w-10 h-10 rounded-xl bg-amber-500/15 dark:bg-amber-400/15 text-amber-800 dark:text-amber-300 border border-amber-500/25 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                              <Icon className="w-5 h-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-[15px] font-bold text-stone-950 dark:text-white group-hover:text-amber-800 dark:group-hover:text-amber-300 transition-colors">
                                  {item.title}
                                </span>
                                <span className={cn(
                                  'text-xs px-2.5 py-0.5 rounded-md font-mono font-bold border shrink-0',
                                  item.badgeColor || 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 border-stone-200 dark:border-stone-700'
                                )}>
                                  {item.badge}
                                </span>
                              </div>
                              <p className="text-xs sm:text-[13px] text-stone-600 dark:text-stone-300 line-clamp-1 mt-1 leading-normal font-medium">
                                {item.desc}
                              </p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              {/* MY TRIP DROPDOWN */}
              <div
                className="relative"
                onMouseEnter={() => handleMouseEnter('mytrip')}
                onMouseLeave={handleMouseLeave}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown('mytrip')}
                  className={cn(
                    'flex items-center gap-2 px-3.5 py-1.5 rounded-full text-[14px] font-bold tracking-tight transition-all duration-200 cursor-pointer',
                    openDropdown === 'mytrip' || pathname.startsWith('/trips') || pathname === '/dashboard' || pathname.startsWith('/safety')
                      ? 'bg-white dark:bg-stone-800 text-stone-950 dark:text-white shadow-xs border border-stone-200/90 dark:border-stone-700'
                      : 'text-stone-750 hover:text-stone-950 dark:text-stone-200 dark:hover:text-white hover:bg-white/60 dark:hover:bg-stone-800/60'
                  )}
                >
                  <Navigation className="w-4 h-4 text-amber-750 dark:text-amber-400" />
                  <span>My Trip</span>
                  <ChevronDown className={cn('w-3.5 h-3.5 transition-transform duration-200 text-stone-400', openDropdown === 'mytrip' && 'rotate-180 text-amber-700 dark:text-amber-400')} />
                </button>

                {openDropdown === 'mytrip' && (
                  <div className="absolute top-full left-0 mt-3 w-[27rem] rounded-2xl bg-[#FCFAF7]/98 dark:bg-[#111622]/98 backdrop-blur-2xl border border-stone-300/90 dark:border-stone-700/80 shadow-[0_24px_50px_-12px_rgba(28,25,23,0.18)] dark:shadow-[0_24px_60px_-12px_rgba(0,0,0,0.7)] p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-200 ring-1 ring-black/5 dark:ring-white/10">
                    <div className="px-3 py-2 text-xs font-extrabold uppercase tracking-wider text-amber-950 dark:text-amber-300 border-b border-stone-200/80 dark:border-stone-800 mb-2.5 flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                        {myTripMenu.title}
                      </span>
                      <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-blue-500/15 text-blue-900 dark:text-blue-300 font-mono font-bold">
                        {myTripMenu.tag}
                      </span>
                    </div>

                    <div className="space-y-2">
                      {myTripMenu.items.map((item) => {
                        const Icon = item.icon;
                        const isCurrent = pathname === item.href;
                        return (
                          <Link
                            key={item.title}
                            href={item.href}
                            className={cn(
                              'group flex items-start gap-3.5 p-3 rounded-xl border transition-all duration-150',
                              isCurrent
                                ? 'bg-amber-500/15 text-amber-950 dark:text-amber-100 border-amber-500/40 shadow-xs'
                                : 'bg-transparent hover:bg-white dark:hover:bg-stone-800/80 border-transparent hover:border-stone-200/90 dark:hover:border-stone-700 hover:shadow-xs text-stone-900 dark:text-stone-100'
                            )}
                          >
                            <div className="w-10 h-10 rounded-xl bg-amber-500/15 dark:bg-amber-400/15 text-amber-800 dark:text-amber-300 border border-amber-500/25 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                              <Icon className="w-5 h-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-[15px] font-bold text-stone-950 dark:text-white group-hover:text-amber-800 dark:group-hover:text-amber-300 transition-colors">
                                  {item.title}
                                </span>
                                <span className={cn(
                                  'text-xs px-2.5 py-0.5 rounded-md font-mono font-bold border shrink-0',
                                  item.badgeColor || 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 border-stone-200 dark:border-stone-700'
                                )}>
                                  {item.badge}
                                </span>
                              </div>
                              <p className="text-xs sm:text-[13px] text-stone-600 dark:text-stone-300 line-clamp-1 mt-1 leading-normal font-medium">
                                {item.desc}
                              </p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

            </nav>

            {/* 3. Right: SOS Red Button (Continuous Infinite Wave Animation) + More Dropdown */}
            <div className="flex items-center gap-2.5">

              {/* SOS Emergency Button with Infinite Radio Tower Animation */}
              <Button
                asChild
                className="bg-gradient-to-r from-red-600 via-rose-600 to-rose-700 hover:from-red-700 hover:to-rose-800 text-white font-black text-xs tracking-wider shadow-md shadow-rose-600/30 border border-rose-400/50 rounded-full px-4 py-2 h-9 sm:h-10 flex items-center gap-2 cursor-pointer transition-all active:scale-95"
              >
                <Link href="/safety/sos">
                  <RadioTower animate={true} loop={true} size={22} className="text-white shrink-0" />
                  <span className="font-mono font-bold text-[13px] tracking-tight">SOS 112</span>
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-90"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
                  </span>
                </Link>
              </Button>

              {/* MORE DROPDOWN */}
              <div
                className="relative hidden sm:block"
                onMouseEnter={() => handleMouseEnter('more')}
                onMouseLeave={handleMouseLeave}
              >
                <button
                  type="button"
                  onClick={() => toggleDropdown('more')}
                  className={cn(
                    'flex items-center gap-1.5 px-3 py-1.5 sm:py-2 rounded-full text-[13px] font-bold tracking-normal transition-all duration-200 border border-stone-300/90 dark:border-stone-700/80 bg-[#EDE9E2]/85 dark:bg-stone-900/80 backdrop-blur-md cursor-pointer',
                    openDropdown === 'more' || pathname.startsWith('/host') || pathname.startsWith('/panchayat') || pathname.startsWith('/admin')
                      ? 'bg-stone-950 dark:bg-white text-white dark:text-stone-950 font-bold shadow-xs'
                      : 'text-stone-800 hover:text-stone-950 dark:text-stone-200 dark:hover:text-white hover:bg-stone-200/80 dark:hover:bg-stone-800'
                  )}
                >
                  <span>More</span>
                  <ChevronDown className={cn('w-3.5 h-3.5 transition-transform duration-200 text-stone-400', openDropdown === 'more' && 'rotate-180')} />
                </button>

                {openDropdown === 'more' && (
                  <div className="absolute top-full right-0 mt-3 w-96 rounded-2xl bg-[#FCFAF7]/98 dark:bg-[#111622]/98 backdrop-blur-2xl border border-stone-300/90 dark:border-stone-700/80 shadow-[0_24px_50px_-12px_rgba(28,25,23,0.18)] dark:shadow-[0_24px_60px_-12px_rgba(0,0,0,0.7)] p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-200 ring-1 ring-black/5 dark:ring-white/10">
                    <div className="px-3 py-2 text-xs font-extrabold uppercase tracking-wider text-amber-950 dark:text-amber-300 border-b border-stone-200/80 dark:border-stone-800 mb-2.5 flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-purple-600"></span>
                        {moreMenu.title}
                      </span>
                      <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-purple-500/15 text-purple-900 dark:text-purple-300 font-mono font-bold">
                        {moreMenu.tag}
                      </span>
                    </div>

                    <div className="space-y-2">
                      {moreMenu.items.map((item) => {
                        const Icon = item.icon;
                        const isCurrent = pathname === item.href;
                        return (
                          <Link
                            key={item.title}
                            href={item.href}
                            className={cn(
                              'group flex items-start gap-3.5 p-3 rounded-xl border transition-all duration-150',
                              isCurrent
                                ? 'bg-amber-500/15 text-amber-950 dark:text-amber-100 border-amber-500/40 shadow-xs'
                                : 'bg-transparent hover:bg-white dark:hover:bg-stone-800/80 border-transparent hover:border-stone-200/90 dark:hover:border-stone-700 hover:shadow-xs text-stone-900 dark:text-stone-100'
                            )}
                          >
                            <div className="w-10 h-10 rounded-xl bg-amber-500/15 dark:bg-amber-400/15 text-amber-800 dark:text-amber-300 border border-amber-500/25 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                              <Icon className="w-5 h-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-[15px] font-bold text-stone-950 dark:text-white group-hover:text-amber-800 dark:group-hover:text-amber-300 transition-colors">
                                  {item.title}
                                </span>
                                <span className="text-xs px-2.5 py-0.5 rounded-md bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 font-mono font-bold border border-stone-200 dark:border-stone-700 shrink-0">
                                  {item.badge}
                                </span>
                              </div>
                              <p className="text-xs sm:text-[13px] text-stone-600 dark:text-stone-300 line-clamp-1 mt-1 leading-normal font-medium">
                                {item.desc}
                              </p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>


              {/* Mobile Menu Toggle Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2.5 rounded-xl text-stone-800 dark:text-stone-200 hover:bg-stone-200/60 dark:hover:bg-stone-800 transition-colors border border-stone-300 dark:border-stone-700"
                aria-label="Toggle navigation"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>

            </div>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-b border-stone-300/80 dark:border-stone-800 bg-[#FAF8F5]/98 dark:bg-[#0E131F]/98 backdrop-blur-2xl px-5 py-5 space-y-4 animate-in fade-in slide-in-from-top-3 duration-200 shadow-2xl max-h-[85vh] overflow-y-auto">

            {/* Mobile Explore Section */}
            <div>
              <span className="text-xs uppercase font-bold text-amber-900 dark:text-amber-400 tracking-wider px-2 block mb-2">
                Explore & Destinations
              </span>
              <div className="space-y-1.5">
                {exploreMenu.items.map((link) => (
                  <Link
                    key={link.title}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all border',
                      pathname === link.href
                        ? 'bg-amber-500/15 dark:bg-amber-950/50 text-amber-950 dark:text-amber-200 border-amber-500/30 font-bold'
                        : 'text-stone-800 dark:text-stone-200 bg-white/60 dark:bg-stone-900/60 border-stone-200/80 dark:border-stone-800 hover:bg-stone-100 dark:hover:bg-stone-800'
                    )}
                  >
                    <span>{link.title}</span>
                    <span className="text-xs font-mono text-stone-500 dark:text-stone-400">{link.badge}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Mobile Plan Section */}
            <div className="pt-3 border-t border-stone-200 dark:border-stone-800">
              <span className="text-xs uppercase font-bold text-amber-900 dark:text-amber-400 tracking-wider px-2 block mb-2">
                Trip Planning
              </span>
              <div className="space-y-1.5">
                {planMenu.items.map((link) => (
                  <Link
                    key={link.title}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all border',
                      pathname === link.href
                        ? 'bg-amber-500/15 dark:bg-amber-950/50 text-amber-950 dark:text-amber-200 border-amber-500/30 font-bold'
                        : 'text-stone-800 dark:text-stone-200 bg-white/60 dark:bg-stone-900/60 border-stone-200/80 dark:border-stone-800 hover:bg-stone-100 dark:hover:bg-stone-800'
                    )}
                  >
                    <span>{link.title}</span>
                    <span className="text-xs font-mono text-stone-500 dark:text-stone-400">{link.badge}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Mobile My Trip Section */}
            <div className="pt-3 border-t border-stone-200 dark:border-stone-800">
              <span className="text-xs uppercase font-bold text-amber-900 dark:text-amber-400 tracking-wider px-2 block mb-2">
                My Trip & Companion
              </span>
              <div className="space-y-1.5">
                {myTripMenu.items.map((link) => (
                  <Link
                    key={link.title}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all border',
                      pathname === link.href
                        ? 'bg-amber-500/15 dark:bg-amber-950/50 text-amber-950 dark:text-amber-200 border-amber-500/30 font-bold'
                        : 'text-stone-800 dark:text-stone-200 bg-white/60 dark:bg-stone-900/60 border-stone-200/80 dark:border-stone-800 hover:bg-stone-100 dark:hover:bg-stone-800'
                    )}
                  >
                    <span>{link.title}</span>
                    <span className="text-xs font-mono text-stone-500 dark:text-stone-400">{link.badge}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Mobile Portals (More) */}
            <div className="pt-3 border-t border-stone-200 dark:border-stone-800">
              <span className="text-xs uppercase font-bold text-amber-900 dark:text-amber-400 tracking-wider px-2 block mb-2">
                Portals & Administration
              </span>
              <div className="space-y-1.5">
                {moreMenu.items.map((link) => {
                  const Icon = link.icon;
                  return (
                    <Link
                      key={link.title}
                      href={link.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium text-stone-800 dark:text-stone-200 bg-white/60 dark:bg-stone-900/60 border border-stone-200/80 dark:border-stone-800 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
                    >
                      <Icon className="w-4 h-4 text-amber-700 dark:text-amber-400" />
                      <span>{link.title}</span>
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* Mobile SOS CTA */}
            <div className="pt-3">
              <Button
                asChild
                className="w-full bg-gradient-to-r from-red-600 via-rose-600 to-rose-700 hover:from-red-700 hover:to-rose-800 text-white font-bold text-sm tracking-wider rounded-2xl py-3 h-12 flex items-center justify-center gap-2 shadow-lg shadow-rose-600/30"
              >
                <Link href="/safety/sos" onClick={() => setMobileMenuOpen(false)}>
                  <RadioTower animate={true} loop={true} size={22} className="text-white shrink-0" />
                  <span>EMERGENCY SOS (DIAL 112)</span>
                </Link>
              </Button>
            </div>

          </div>
        )}
      </header>

      {/* Modern Mobile Bottom Navigation Dock */}
      <div className="lg:hidden fixed bottom-3 left-4 right-4 z-40">
        <div className="glass-panel rounded-2xl p-2 flex items-center justify-around shadow-xl border border-stone-300/80 dark:border-stone-700/80 bg-[#FAF8F5]/90 dark:bg-[#0E131F]/90 backdrop-blur-xl">
          <Link
            href="/"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname === '/'
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-600 hover:text-stone-950 dark:text-stone-400'
            )}
          >
            <Compass className="w-4 h-4" />
            <span className="text-[11px] font-medium mt-0.5">Explore</span>
          </Link>

          <Link
            href="/itinerary"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname === '/itinerary'
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-600 hover:text-stone-950 dark:text-stone-400'
            )}
          >
            <Calendar className="w-4 h-4" />
            <span className="text-[11px] font-medium mt-0.5">Plan</span>
          </Link>

          <Link
            href="/trips"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname.startsWith('/trips')
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-600 hover:text-stone-950 dark:text-stone-400'
            )}
          >
            <Navigation className="w-4 h-4" />
            <span className="text-[11px] font-medium mt-0.5">My Trip</span>
          </Link>

          <Link
            href="/destinations/darjeeling/alternatives"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname.includes('/alternatives')
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-600 hover:text-stone-950 dark:text-stone-400'
            )}
          >
            <Sparkles className="w-4 h-4" />
            <span className="text-[11px] font-medium mt-0.5">Alternatives</span>
          </Link>

          <Link
            href="/safety/sos"
            className="flex flex-col items-center py-1 px-3 rounded-xl text-rose-600 dark:text-rose-400 font-bold"
          >
            <ShieldAlert className="w-4 h-4" />
            <span className="text-[11px] font-bold mt-0.5">SOS</span>
          </Link>
        </div>
      </div>
    </>
  );
};
