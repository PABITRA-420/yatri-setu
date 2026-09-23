'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Compass, Calendar, LayoutDashboard, ShieldAlert } from 'lucide-react';

export function MobileBottomNav() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/destinations', label: 'Explore', icon: Compass },
    { href: '/itinerary', label: 'Planner', icon: Calendar },
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/safety/sos', label: 'Safety', icon: ShieldAlert, highlight: true }
  ];

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-stone-950/90 backdrop-blur-xl border-t border-white/10 px-3 py-2 flex items-center justify-around shadow-2xl">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));

        if (item.highlight) {
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center justify-center p-2 rounded-2xl transition-all ${
                isActive
                  ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30'
                  : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
              }`}
            >
              <Icon className="w-5 h-5 animate-pulse" />
              <span className="text-[10px] font-extrabold mt-0.5">{item.label}</span>
            </Link>
          );
        }

        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all ${
              isActive
                ? 'text-amber-400 font-bold scale-105'
                : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            <Icon className="w-5 h-5" />
            <span className="text-[10px] font-medium mt-0.5 tracking-tight">{item.label}</span>
          </Link>
        );
      })}
    </div>
  );
}
