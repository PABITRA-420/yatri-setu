'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';

export function Breadcrumbs() {
  const pathname = usePathname();

  if (!pathname || pathname === '/') return null;

  const segments = pathname.split('/').filter(Boolean);

  const getLabel = (seg: string) => {
    switch (seg) {
      case 'destinations': return 'Destinations';
      case 'homestays': return 'Homestays';
      case 'itinerary': return 'AI Itinerary';
      case 'dashboard': return 'Dashboard';
      case 'host': return 'Host Portal';
      case 'panchayat': return 'Panchayat Desk';
      case 'safety': return 'Safety';
      case 'sos': return 'SOS Telemetry';
      case 'booking': return 'Booking';
      case 'confirmation': return 'Confirmation';
      default: return seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' ');
    }
  };

  return (
    <nav className="flex items-center gap-1.5 text-xs text-stone-400 py-2 overflow-x-auto scrollbar-none">
      <Link href="/" className="hover:text-amber-400 transition-colors flex items-center gap-1">
        <Home className="w-3.5 h-3.5" />
        <span>Home</span>
      </Link>
      {segments.map((seg, idx) => {
        const href = '/' + segments.slice(0, idx + 1).join('/');
        const isLast = idx === segments.length - 1;
        const label = getLabel(seg);

        return (
          <React.Fragment key={href}>
            <ChevronRight className="w-3 h-3 text-stone-600 shrink-0" />
            {isLast ? (
              <span className="font-semibold text-amber-300 truncate max-w-[180px] sm:max-w-none">
                {label}
              </span>
            ) : (
              <Link href={href} className="hover:text-stone-200 transition-colors truncate max-w-[140px] sm:max-w-none">
                {label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
