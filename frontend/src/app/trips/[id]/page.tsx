'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { TripDetailsResponse } from '@/types';
import { fetchTripDetails } from '@/lib/api';
import { 
  ShieldAlert, 
  MapPin, 
  Calendar, 
  Phone, 
  QrCode, 
  Sun, 
  CheckSquare, 
  Square, 
  AlertTriangle, 
  ArrowRight,
  Sparkles,
  Users
} from 'lucide-react';

export default function TripDashboardPage() {
  const params = useParams();
  const tripId = typeof params?.id === 'string' ? params.id : 'demo-kalimpong';

  const [trip, setTrip] = useState<TripDetailsResponse | null>(null);
  const [checkedItems, setCheckedItems] = useState<number[]>([0, 1]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchTripDetails(tripId);
      setTrip(data);
      setLoading(false);
    }
    load();
  }, [tripId]);

  const toggleCheck = (idx: number) => {
    if (checkedItems.includes(idx)) {
      setCheckedItems(checkedItems.filter((i) => i !== idx));
    } else {
      setCheckedItems([...checkedItems, idx]);
    }
  };

  if (loading || !trip) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center animate-pulse">
        <div className="h-10 w-64 bg-slate-200 dark:bg-slate-800 rounded-xl mx-auto mb-4" />
        <div className="h-6 w-96 bg-slate-200 dark:bg-slate-800 rounded-lg mx-auto" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Active Trip Header */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
              Active Trip Companion
            </span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black tracking-tight">
            Journey to {trip.destination_name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span>{trip.homestay_name} • {trip.dates}</span>
          </p>
        </div>

        {/* SOS Emergency Trigger Button */}
        <Link
          href="/safety/sos"
          className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-700 hover:to-red-700 text-white font-extrabold text-xs shadow-lg shadow-rose-600/40 active:scale-95 transition-all flex items-center gap-2 self-start md:self-auto"
        >
          <ShieldAlert className="w-5 h-5 animate-pulse" />
          <span>TRIGGER SOS RESCUE BEACON</span>
        </Link>
      </div>

      {/* Main Grid: Digital Pass & Live Safety Info */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Digital Pass Card (Left 5 Cols) */}
        <div className="lg:col-span-5 bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Panchayat Pass Verification
              </span>
              <span className="text-xs font-mono font-bold text-amber-600 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                {trip.digital_pass_code}
              </span>
            </div>

            {/* QR Visual */}
            <div className="w-40 h-40 bg-white p-3 rounded-2xl border border-slate-200 shadow-inner mx-auto flex items-center justify-center">
              <QrCode className="w-32 h-32 text-slate-900" />
            </div>

            <p className="text-center text-[11px] text-slate-400 mt-3">
              Valid at Teesta Checkpost, Forest Entry Gates & Homestay Check-in
            </p>

            {/* Emergency Contacts */}
            <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between text-slate-600 dark:text-slate-300">
                <span className="flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Host Support:</span>
                </span>
                <span className="font-bold text-slate-900 dark:text-white">{trip.host_support_number}</span>
              </div>
              <div className="flex items-center justify-between text-slate-600 dark:text-slate-300">
                <span className="flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-amber-500" />
                  <span>Panchayat Desk:</span>
                </span>
                <span className="font-bold text-slate-900 dark:text-white">{trip.local_panchayat_contact}</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">
            <span>✓ GPS Pin Geofence Active</span>
            <span>✓ Low Mountain Footfall Tracked</span>
          </div>
        </div>

        {/* Right 7 Cols: Weather Alert, Packing Checklist, Itinerary Link */}
        <div className="lg:col-span-7 space-y-6">
          {/* Weather Advisory */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-5 flex items-start gap-3">
            <div className="p-2 rounded-xl bg-amber-500 text-white shrink-0 mt-0.5">
              <Sun className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                Live Mountain Weather & Trail Outlook
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-0.5">
                {trip.weather_alert}
              </p>
            </div>
          </div>

          {/* Packing & Eco Guidelines Checklist */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-base text-slate-900 dark:text-white">
                Traveler Checklist & Eco Guidelines
              </h3>
              <span className="text-xs text-slate-400">
                {checkedItems.length} of {trip.packing_checklist.length} packed
              </span>
            </div>

            <div className="space-y-2.5">
              {trip.packing_checklist.map((item, idx) => {
                const isChecked = checkedItems.includes(idx);
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => toggleCheck(idx)}
                    className="w-full flex items-start gap-2.5 text-left p-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors"
                  >
                    {isChecked ? (
                      <CheckSquare className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                    )}
                    <span className={`text-xs ${isChecked ? 'line-through text-slate-400' : 'text-slate-700 dark:text-slate-300'}`}>
                      {item}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Quick Shortcuts */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link
              href="/itinerary?destination=kalimpong"
              className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:border-amber-500/40 transition-colors flex items-center justify-between"
            >
              <div>
                <span className="text-xs font-bold text-slate-900 dark:text-white block">
                  3-Day Itinerary Schedule
                </span>
                <span className="text-[11px] text-slate-500">View morning & evening activities</span>
              </div>
              <ArrowRight className="w-4 h-4 text-amber-600" />
            </Link>

            <Link
              href="/safety/sos"
              className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 shadow-sm hover:bg-rose-500/20 transition-colors flex items-center justify-between text-rose-700 dark:text-rose-400"
            >
              <div>
                <span className="text-xs font-bold block">
                  Safety SOS Simulator
                </span>
                <span className="text-[11px] opacity-80">Test live responder dispatch</span>
              </div>
              <ShieldAlert className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
