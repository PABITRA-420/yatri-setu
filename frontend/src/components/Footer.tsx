import React from 'react';
import Link from 'next/link';
import { ArrowUpRight, Leaf } from 'lucide-react';

export const Footer: React.FC = () => (
  <footer className="bg-[#183A32] text-white">
    <div className="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-10 lg:py-20">
      <div className="grid gap-12 md:grid-cols-[1.4fr_.8fr_.8fr_.8fr]">
        <div>
          <div className="mb-5 text-xl font-semibold tracking-[-.04em]">YATRI SETU</div>
          <h2 className="max-w-md font-editorial text-4xl leading-[.95] sm:text-5xl">Travel locally. Discover meaningfully.</h2>
          <p className="mt-5 max-w-sm text-sm leading-6 text-white/60">A calmer way to discover destinations, local stays and experiences while helping distribute tourist pressure.</p>
        </div>
        <div>
          <div className="mb-4 text-[9px] font-bold uppercase tracking-[.2em] text-white/40">Explore</div>
          <div className="space-y-3 text-sm text-white/70">
            <Link className="block hover:text-white" href="/destinations">Destinations</Link>
            <Link className="block hover:text-white" href="/homestays">Local stays</Link>
            <Link className="block hover:text-white" href="/itinerary">Plan a journey</Link>
          </div>
        </div>
        <div>
          <div className="mb-4 text-[9px] font-bold uppercase tracking-[.2em] text-white/40">Travel better</div>
          <div className="space-y-3 text-sm text-white/70">
            <Link className="block hover:text-white" href="/destinations/darjeeling/crowd">Crowd intelligence</Link>
            <Link className="block hover:text-white" href="/destinations/darjeeling/alternatives">Quiet alternatives</Link>
            <Link className="block hover:text-white" href="/dashboard">Green Credits</Link>
          </div>
        </div>
        <div>
          <div className="mb-4 text-[9px] font-bold uppercase tracking-[.2em] text-white/40">Safety</div>
          <Link href="/safety/sos" className="inline-flex items-center gap-2 text-sm font-semibold text-white hover:text-[#E7EEE9]">Emergency SOS <ArrowUpRight className="h-4 w-4" /></Link>
          <div className="mt-4 flex items-center gap-2 text-xs text-white/55"><Leaf className="h-4 w-4" /> Built around responsible travel</div>
        </div>
      </div>
      <div className="mt-14 flex flex-col gap-3 border-t border-white/10 pt-5 text-[10px] uppercase tracking-[.12em] text-white/35 sm:flex-row sm:items-center sm:justify-between">
        <span>© 2026 Yatri Setu</span><span>Travel slower. Discover locally.</span>
      </div>
    </div>
  </footer>
);
