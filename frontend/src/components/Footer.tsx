import React from 'react';
import Link from 'next/link';
import { Heart, Compass, Shield, Users, Leaf } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-600 dark:text-slate-400 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Col 1: Brand & Purpose */}
          <div className="md:col-span-1 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-amber-600 to-rose-500 flex items-center justify-center text-white font-bold text-sm">
                YS
              </div>
              <span className="font-extrabold text-lg text-slate-900 dark:text-white">
                Yatri Setu
              </span>
            </div>
            <p className="text-xs leading-relaxed text-slate-500">
              Active tourist flow management & rural empowerment. Preventing overtourism at fragile Himalayan hotspots while uplifting local homestay economies.
            </p>
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
              <Leaf className="w-4 h-4" />
              <span>Smart India Hackathon 2026</span>
            </div>
          </div>

          {/* Col 2: Crowd Advisor & Demo */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Smart Flow Engine
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/destinations/darjeeling/crowd" className="hover:text-amber-600 transition-colors">
                  Darjeeling Crowd Intelligence
                </Link>
              </li>
              <li>
                <Link href="/destinations/darjeeling/alternatives" className="hover:text-amber-600 transition-colors">
                  Kalimpong Similarity Advisor
                </Link>
              </li>
              <li>
                <Link href="/destinations" className="hover:text-amber-600 transition-colors">
                  Multi-Factor Footfall Heatmap
                </Link>
              </li>
              <li>
                <Link href="/itinerary" className="hover:text-amber-600 transition-colors">
                  AI Crowd-Avoiding Itinerary
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Rural Homestays */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Hyperlocal Community
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/homestays" className="hover:text-amber-600 transition-colors">
                  Verified Panchayat Stays
                </Link>
              </li>
              <li>
                <Link href="/homestays" className="hover:text-amber-600 transition-colors">
                  Community Development Fund (10%)
                </Link>
              </li>
              <li>
                <Link href="/trips/demo-kalimpong" className="hover:text-amber-600 transition-colors">
                  Active Travel Companion Pass
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: Safety & Support */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Traveler Safety
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/safety/sos" className="text-rose-600 dark:text-rose-400 font-semibold hover:underline">
                  Live SOS Emergency Broadcast
                </Link>
              </li>
              <li className="text-slate-500">
                National Helpline: <span className="font-bold text-slate-800 dark:text-slate-200">112</span>
              </li>
              <li className="text-slate-500">
                Tourist Safety: <span className="font-bold text-slate-800 dark:text-slate-200">1363</span>
              </li>
              <li className="text-slate-500">
                Offline Digital Travel Pass Verified
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-3">
          <p>© 2026 Yatri Setu • Smart India Hackathon Project</p>
          <div className="flex items-center gap-1">
            <span>Built for sustainable Indian tourism with</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline" />
          </div>
        </div>
      </div>
    </footer>
  );
};
