'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Compass, 
  ShieldAlert, 
  MapPin, 
  Calendar, 
  Home, 
  Sparkles, 
  Menu, 
  X,
  Flame,
  UserCheck,
  Landmark,
  Activity,
  ArrowUpRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const primaryNav = [
    { name: 'Explore', href: '/destinations' },
    { name: 'Crowd Advisor', href: '/destinations/darjeeling/crowd' },
    { name: 'Alternatives', href: '/destinations/darjeeling/alternatives' },
    { name: 'AI Itinerary', href: '/itinerary' },
    { name: 'Homestays', href: '/homestays' },
  ];

  const secondaryNav = [
    { name: 'Host Portal', href: '/host', icon: UserCheck },
    { name: 'Panchayat', href: '/panchayat', icon: Landmark },
    { name: 'Command Center', href: '/admin/command-center', icon: Activity },
  ];

  return (
    <>
      <header
        className={cn(
          'sticky top-0 z-50 transition-all duration-300',
          scrolled
            ? 'bg-white/90 dark:bg-[#0B0F17]/90 backdrop-blur-md border-b border-stone-200/80 dark:border-white/10 shadow-xs'
            : 'bg-transparent border-b border-transparent backdrop-blur-xs'
        )}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Brand Logo Lockup */}
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-stone-900 dark:bg-white text-white dark:text-stone-950 flex items-center justify-center font-bold text-sm tracking-wider shadow-sm transition-transform duration-300 group-hover:scale-105 border border-stone-800 dark:border-stone-200">
                YS
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-xl tracking-tight text-stone-900 dark:text-white group-hover:text-amber-700 dark:group-hover:text-amber-400 transition-colors">
                    Yatri<span className="font-editorial italic font-normal text-amber-700 dark:text-amber-400 ml-0.5">Setu</span>
                  </span>
                </div>
                <span className="text-[10px] text-stone-500 dark:text-stone-400 tracking-wide font-medium hidden sm:block">
                  Himalayan Flow Intelligence
                </span>
              </div>
            </Link>

            {/* Desktop Center Navigation */}
            <nav className="hidden lg:flex items-center gap-1 bg-stone-100/80 dark:bg-stone-900/80 p-1.5 rounded-full border border-stone-200/70 dark:border-white/10 backdrop-blur-md">
              {primaryNav.map((link) => {
                const isActive =
                  pathname === link.href ||
                  (link.href !== '/' && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className={cn(
                      'px-4 py-1.5 rounded-full text-xs font-semibold tracking-tight transition-all duration-200',
                      isActive
                        ? 'bg-white dark:bg-stone-800 text-stone-950 dark:text-white shadow-xs font-bold'
                        : 'text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-white hover:bg-stone-200/50 dark:hover:bg-stone-800/50'
                    )}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </nav>

            {/* Right Side: Command/Host Portal Dropdown & SOS Pill */}
            <div className="flex items-center gap-2.5 sm:gap-3">
              {/* Secondary Portals (Desktop) */}
              <div className="hidden xl:flex items-center gap-1 text-xs">
                <Link
                  href="/admin/command-center"
                  className="px-3 py-1.5 rounded-lg text-stone-600 dark:text-stone-400 hover:text-stone-950 dark:hover:text-white hover:bg-stone-100 dark:hover:bg-stone-900 transition-colors font-medium flex items-center gap-1"
                >
                  <Activity className="w-3.5 h-3.5 text-amber-600" />
                  <span>Ops Center</span>
                </Link>
                <Link
                  href="/panchayat"
                  className="px-3 py-1.5 rounded-lg text-stone-600 dark:text-stone-400 hover:text-stone-950 dark:hover:text-white hover:bg-stone-100 dark:hover:bg-stone-900 transition-colors font-medium flex items-center gap-1"
                >
                  <Landmark className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Panchayat</span>
                </Link>
              </div>

              {/* SOS Quick Button */}
              <Link
                href="/safety/sos"
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-rose-700 hover:bg-rose-800 text-white text-[11px] font-bold tracking-wider shadow-xs hover:shadow-sm active:scale-97 transition-all border border-rose-600/40"
              >
                <span className="w-2 h-2 rounded-full bg-rose-300 animate-pulse" />
                <span className="font-mono">SOS 112</span>
              </Link>

              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-xl text-stone-700 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
                aria-label="Toggle navigation"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-b border-stone-200/80 dark:border-white/10 bg-white/95 dark:bg-[#0B0F17]/95 backdrop-blur-xl px-5 py-4 space-y-2 animate-fadeIn shadow-lg">
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider px-3 block mb-1">
                Navigation
              </span>
              {primaryNav.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all',
                      isActive
                        ? 'bg-stone-100 dark:bg-stone-800 text-stone-950 dark:text-white font-bold'
                        : 'text-stone-600 dark:text-stone-400 hover:bg-stone-50 dark:hover:bg-stone-900'
                    )}
                  >
                    <span>{link.name}</span>
                    <ArrowUpRight className="w-4 h-4 text-stone-400" />
                  </Link>
                );
              })}
            </div>

            <div className="pt-3 border-t border-stone-100 dark:border-stone-800 space-y-1">
              <span className="text-[10px] uppercase font-bold text-stone-400 tracking-wider px-3 block mb-1">
                Portals & Administration
              </span>
              {secondaryNav.map((link) => {
                const Icon = link.icon;
                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-medium text-stone-600 dark:text-stone-400 hover:bg-stone-50 dark:hover:bg-stone-900 transition-colors"
                  >
                    <Icon className="w-4 h-4 text-amber-600" />
                    <span>{link.name}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </header>

      {/* Modern Mobile Bottom Navigation Dock */}
      <div className="lg:hidden fixed bottom-3 left-4 right-4 z-40">
        <div className="glass-panel rounded-2xl p-1.5 flex items-center justify-around shadow-xl border border-stone-200/80 dark:border-white/10">
          <Link
            href="/"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname === '/'
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-500 hover:text-stone-900 dark:text-stone-400'
            )}
          >
            <Compass className="w-4 h-4" />
            <span className="text-[10px] mt-0.5">Explore</span>
          </Link>

          <Link
            href="/destinations/darjeeling/crowd"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname.includes('/crowd')
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-500 hover:text-stone-900 dark:text-stone-400'
            )}
          >
            <Flame className="w-4 h-4" />
            <span className="text-[10px] mt-0.5">Crowd</span>
          </Link>

          <Link
            href="/destinations/darjeeling/alternatives"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname.includes('/alternatives')
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-500 hover:text-stone-900 dark:text-stone-400'
            )}
          >
            <Sparkles className="w-4 h-4" />
            <span className="text-[10px] mt-0.5">Alternatives</span>
          </Link>

          <Link
            href="/homestays"
            className={cn(
              'flex flex-col items-center py-1 px-3 rounded-xl transition-colors',
              pathname.includes('/homestays')
                ? 'text-amber-700 dark:text-amber-400 font-bold'
                : 'text-stone-500 hover:text-stone-900 dark:text-stone-400'
            )}
          >
            <Home className="w-4 h-4" />
            <span className="text-[10px] mt-0.5">Stays</span>
          </Link>

          <Link
            href="/safety/sos"
            className="flex flex-col items-center py-1 px-3 rounded-xl text-rose-600 dark:text-rose-400 font-bold"
          >
            <ShieldAlert className="w-4 h-4" />
            <span className="text-[10px] mt-0.5">SOS</span>
          </Link>
        </div>
      </div>
    </>
  );
};

