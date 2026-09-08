'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Home, 
  ShieldCheck, 
  Leaf, 
  Clock, 
  CheckCircle2, 
  ArrowLeft, 
  Plus, 
  Sparkles,
  MapPin,
  Eye,
  AlertCircle
} from 'lucide-react';
import { fetchHostListings } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { HomestayListing } from '@/types';

export default function HostListingsPage() {
  const [listings, setListings] = useState<HomestayListing[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchHostListings('host-kalim-01');
        setListings(data);
      } catch (err) {
        console.error('Failed to load listings:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PUBLISHED':
      case 'VERIFIED':
        return (
          <span className="px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-bold text-[10px] tracking-wide border border-emerald-500/30 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>PANCHAYAT VERIFIED & LIVE</span>
          </span>
        );
      case 'UNDER_REVIEW':
        return (
          <span className="px-2.5 py-1 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 font-bold text-[10px] tracking-wide border border-amber-500/30 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-amber-600" />
            <span>CIVIC INSPECTION UNDERWAY</span>
          </span>
        );
      case 'SUBMITTED':
        return (
          <span className="px-2.5 py-1 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 font-bold text-[10px] tracking-wide border border-blue-500/30 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-blue-600" />
            <span>SUBMITTED TO PANCHAYAT</span>
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 font-bold text-[10px] tracking-wide border border-rose-500/30 flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>{status}</span>
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <Link href="/host/dashboard" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-amber-600 transition-colors mb-2">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Dashboard</span>
            </Link>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
              My Homestay Properties
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Manage your verified village accommodation and guest availability
            </p>
          </div>

          <Link
            href="/host/onboarding"
            className="px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-md shadow-amber-600/20 flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>List New Property</span>
          </Link>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-amber-600 mx-auto" />
          </div>
        ) : listings.length === 0 ? (
          <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 space-y-4">
            <Home className="w-12 h-12 text-slate-400 mx-auto" />
            <p className="text-slate-600 dark:text-slate-400 text-sm">No homestays listed yet.</p>
            <Link
              href="/host/onboarding"
              className="inline-block px-4 py-2 rounded-xl bg-amber-600 text-white font-bold text-xs"
            >
              Start Onboarding
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {listings.map((l) => (
              <div
                key={l.id}
                className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-md transition-all p-6 space-y-6"
              >
                <div className="flex flex-col md:flex-row gap-6">
                  {/* Photo Thumbnail */}
                  <img
                    src={l.images[0] || 'https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=600&q=80'}
                    alt={l.title}
                    className="w-full md:w-64 h-48 rounded-2xl object-cover"
                  />

                  {/* Details */}
                  <div className="flex-1 space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {getStatusBadge(l.verification_status)}
                        <span className="text-xs font-mono text-slate-400">{l.id}</span>
                      </div>
                      <div className="text-lg font-black text-slate-900 dark:text-white">
                        {formatINR(l.price_per_night_inr)} <span className="text-xs text-slate-400 font-normal">/ night</span>
                      </div>
                    </div>

                    <div>
                      <h2 className="text-lg font-black text-slate-900 dark:text-white">
                        {l.title}
                      </h2>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        {l.tagline}
                      </p>
                      <div className="flex items-center gap-1 text-xs text-slate-600 dark:text-slate-300 mt-1">
                        <MapPin className="w-3.5 h-3.5 text-amber-500" />
                        <span>{l.village}, {l.panchayat_name} ({l.destination_name})</span>
                      </div>
                    </div>

                    {/* Amenities & Sustainability */}
                    <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                      <div className="flex flex-wrap gap-1.5">
                        {l.amenities.map((a, i) => (
                          <span key={i} className="text-[10px] bg-slate-100 dark:bg-slate-800 px-2.5 py-0.5 rounded text-slate-600 dark:text-slate-300">
                            {a}
                          </span>
                        ))}
                      </div>

                      <div className="flex flex-wrap gap-1.5">
                        {l.sustainability_attributes.map((s, i) => (
                          <span key={i} className="text-[10px] bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 border border-teal-500/20 px-2 py-0.5 rounded flex items-center gap-1">
                            <Leaf className="w-2.5 h-2.5" />
                            <span>{s}</span>
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Bottom Actions */}
                    <div className="pt-3 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 dark:border-slate-800">
                      <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold">
                        Host Retention: 90% (₹{(l.price_per_night_inr * 0.9).toFixed(0)}/nt)
                      </span>

                      <div className="flex items-center gap-2">
                        <Link
                          href={`/homestays`}
                          className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 font-bold text-xs flex items-center gap-1"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Public Page</span>
                        </Link>
                        <Link
                          href="/host/availability"
                          className="px-3 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs"
                        >
                          Manage Calendar
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
