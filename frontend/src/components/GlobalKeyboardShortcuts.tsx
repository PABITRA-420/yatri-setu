'use client';

import React, { useState, useEffect } from 'react';
import { Search, Compass, Calendar, Home, ShieldAlert, X } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function GlobalKeyboardShortcuts() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((prev) => !prev);
      } else if (e.key === 'Escape') {
        setOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const shortcuts = [
    { label: 'Explore Destinations', href: '/destinations', icon: Compass },
    { label: 'AI Itinerary Planner', href: '/itinerary', icon: Calendar },
    { label: 'Verified Homestays', href: '/homestays', icon: Home },
    { label: 'Emergency SOS Safety', href: '/safety/sos', icon: ShieldAlert },
    { label: 'Tourist Dashboard', href: '/dashboard', icon: Search }
  ];

  const filtered = shortcuts.filter((s) =>
    s.label.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (href: string) => {
    setOpen(false);
    setSearch('');
    router.push(href);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-stone-950/80 backdrop-blur-md flex items-start justify-center pt-24 px-4">
      <div className="bg-stone-900 border border-white/15 rounded-3xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="p-4 border-b border-white/10 flex items-center gap-3">
          <Search className="w-5 h-5 text-amber-400 shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search Yatri Setu routes, destinations... (Cmd+K)"
            className="w-full bg-transparent text-sm text-white placeholder:text-stone-500 focus:outline-none"
            autoFocus
          />
          <button
            onClick={() => setOpen(false)}
            className="p-1 text-stone-400 hover:text-white rounded-lg hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-2 max-h-80 overflow-y-auto space-y-1">
          {filtered.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.href}
                onClick={() => handleSelect(item.href)}
                className="w-full text-left flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold text-stone-300 hover:text-white hover:bg-amber-500/15 border border-transparent hover:border-amber-500/30 transition-all"
              >
                <Icon className="w-4 h-4 text-amber-400 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
          {filtered.length === 0 && (
            <div className="py-8 text-center text-xs text-stone-500">
              No matching pages found for "{search}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
