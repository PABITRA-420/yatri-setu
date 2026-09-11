import React from 'react';
import Link from 'next/link';
import { Heart, Compass, Shield, Users, Leaf, ArrowUpRight } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-stone-200/80 dark:border-white/10 bg-stone-100/60 dark:bg-[#070A0F] text-stone-600 dark:text-stone-400 py-16 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
          {/* Col 1: Brand & Purpose */}
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-stone-900 dark:bg-white text-white dark:text-stone-950 flex items-center justify-center font-bold text-sm shadow-xs border border-stone-800 dark:border-stone-200">
                YS
              </div>
              <span className="font-extrabold text-xl text-stone-950 dark:text-white tracking-tight">
                Yatri<span className="font-editorial italic font-normal text-amber-700 dark:text-amber-400 ml-0.5">Setu</span>
              </span>
            </div>
            <p className="text-xs leading-relaxed text-stone-500 dark:text-stone-400">
              Active tourist flow management and rural regeneration. Intelligently mitigating overtourism across vulnerable Himalayan circuits while uplifting local panchayat homestays.
            </p>
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
              <Leaf className="w-4 h-4" />
              <span>Smart India Hackathon 2026 Core Solution</span>
            </div>
          </div>

          {/* Col 2: Crowd Advisor & Demo */}
          <div>
            <h4 className="text-[11px] font-bold uppercase tracking-widest text-stone-950 dark:text-white mb-4">
              Smart Flow Engine
            </h4>
            <ul className="space-y-2.5 text-xs">
              <li>
                <Link href="/destinations/darjeeling/crowd" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  Darjeeling Crowd Intelligence
                </Link>
              </li>
              <li>
                <Link href="/destinations/darjeeling/alternatives" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  Kalimpong Similarity Advisor
                </Link>
              </li>
              <li>
                <Link href="/destinations" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  Multi-Factor Footfall Catalog
                </Link>
              </li>
              <li>
                <Link href="/itinerary" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  Adaptive AI Travel Itinerary
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Rural Homestays */}
          <div>
            <h4 className="text-[11px] font-bold uppercase tracking-widest text-stone-950 dark:text-white mb-4">
              Hyperlocal Community
            </h4>
            <ul className="space-y-2.5 text-xs">
              <li>
                <Link href="/homestays" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  Verified Panchayat Stays
                </Link>
              </li>
              <li>
                <Link href="/homestays" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  10% Village Development Fund
                </Link>
              </li>
              <li>
                <Link href="/host" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  Host Management Portal
                </Link>
              </li>
              <li>
                <Link href="/panchayat" className="hover:text-amber-700 dark:hover:text-amber-400 transition-colors">
                  Gram Panchayat Verifications
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: Traveler Safety & Helpline */}
          <div>
            <h4 className="text-[11px] font-bold uppercase tracking-widest text-stone-950 dark:text-white mb-4">
              Safety & Emergency
            </h4>
            <ul className="space-y-2.5 text-xs">
              <li>
                <Link href="/safety/sos" className="text-rose-700 dark:text-rose-400 font-bold hover:underline flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                  <span>Live Emergency SOS Dispatch</span>
                </Link>
              </li>
              <li className="text-stone-500 dark:text-stone-400">
                National Emergency: <span className="font-bold text-stone-900 dark:text-stone-200 font-mono">112</span>
              </li>
              <li className="text-stone-500 dark:text-stone-400">
                Tourist Safety Helpline: <span className="font-bold text-stone-900 dark:text-stone-200 font-mono">1363</span>
              </li>
              <li className="text-stone-500 dark:text-stone-400">
                Yatri Mitra Verified Community Network
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-stone-200 dark:border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-stone-400 gap-3">
          <p>© 2026 Yatri Setu • Smart India Hackathon Project</p>
          <div className="flex items-center gap-1">
            <span>Preserving Himalayan sanctuaries with regenerative travel</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

