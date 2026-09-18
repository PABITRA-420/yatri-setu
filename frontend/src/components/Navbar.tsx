'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, ArrowUpRight, ShieldAlert, Compass, CalendarDays, Home, Sparkles, UserRound } from 'lucide-react';
import { cn } from '@/lib/utils';

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const nav = [
    { name: 'Explore', href: '/destinations' },
    { name: 'Plan', href: '/itinerary' },
    { name: 'Stays', href: '/homestays' },
    { name: 'Crowd', href: '/destinations/darjeeling/crowd' },
  ];

  return (
    <>
      <header className={cn(
        'fixed inset-x-0 top-0 z-50 transition-all duration-500',
        scrolled ? 'bg-[#F5F2EA]/88 backdrop-blur-xl border-b border-black/[.06]' : 'bg-transparent'
      )}>
        <div className="mx-auto flex h-[76px] max-w-7xl items-center justify-between px-5 sm:px-8 lg:px-10">
          <Link href="/" className="group flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#183A32] text-[10px] font-bold tracking-[.12em] text-white transition-transform duration-300 group-hover:scale-105">YS</div>
            <div>
              <div className="text-[17px] font-semibold tracking-[-.04em] text-[#171714]">YATRI SETU</div>
              <div className="hidden text-[8px] font-semibold uppercase tracking-[.22em] text-black/40 sm:block">Intelligent travel</div>
            </div>
          </Link>

          <nav className="hidden items-center gap-7 lg:flex">
            {nav.map((item) => {
              const active = pathname === item.href || pathname.startsWith(item.href + '/');
              return (
                <Link key={item.href} href={item.href} className={cn(
                  'text-[11px] font-semibold transition-colors',
                  active ? 'text-[#183A32]' : 'text-black/55 hover:text-black'
                )}>
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            <Link href="/dashboard" className="hidden rounded-full px-3 py-2 text-[10px] font-bold text-black/60 transition hover:bg-black/5 hover:text-black sm:flex sm:items-center sm:gap-1.5">
              <UserRound className="h-3.5 w-3.5" /> My journey
            </Link>
            <Link href="/safety/sos" className="hidden items-center gap-1.5 rounded-full bg-[#B94A48] px-4 py-2.5 text-[10px] font-bold tracking-[.08em] text-white transition hover:bg-[#a33f3d] sm:flex">
              <span className="h-1.5 w-1.5 animate-soft-pulse rounded-full bg-white" /> SOS
            </Link>
            <button onClick={() => setOpen(!open)} className="rounded-full p-2.5 text-black lg:hidden" aria-label="Toggle navigation">
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {open && (
          <div className="border-t border-black/[.06] bg-[#F5F2EA]/96 px-5 py-5 backdrop-blur-xl lg:hidden">
            <div className="space-y-1">
              {nav.map((item) => (
                <Link key={item.href} href={item.href} onClick={() => setOpen(false)} className="flex items-center justify-between rounded-2xl px-4 py-3.5 text-sm font-semibold hover:bg-black/[.04]">
                  {item.name}<ArrowUpRight className="h-4 w-4 text-black/35" />
                </Link>
              ))}
              <Link href="/dashboard" onClick={() => setOpen(false)} className="flex items-center justify-between rounded-2xl px-4 py-3.5 text-sm font-semibold hover:bg-black/[.04]">My journey<ArrowUpRight className="h-4 w-4 text-black/35" /></Link>
              <Link href="/safety/sos" onClick={() => setOpen(false)} className="mt-2 flex items-center justify-between rounded-2xl bg-[#B94A48] px-4 py-3.5 text-sm font-bold text-white">Emergency SOS<ShieldAlert className="h-4 w-4" /></Link>
            </div>
          </div>
        )}
      </header>

      <div className="fixed bottom-4 left-4 right-4 z-40 lg:hidden">
        <div className="mx-auto flex max-w-md items-center justify-around rounded-[22px] border border-white/20 bg-[#183A32]/95 p-2 shadow-2xl backdrop-blur-xl">
          {[
            { href: '/destinations', label: 'Explore', icon: Compass },
            { href: '/itinerary', label: 'Plan', icon: CalendarDays },
            { href: '/homestays', label: 'Stay', icon: Home },
            { href: '/dashboard', label: 'Journey', icon: Sparkles },
          ].map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link key={item.href} href={item.href} className={cn('flex min-w-[62px] flex-col items-center gap-1 rounded-2xl px-3 py-2 text-white/55 transition', active && 'bg-white/10 text-white')}>
                <Icon className="h-4 w-4" />
                <span className="text-[9px] font-semibold">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </>
  );
};
