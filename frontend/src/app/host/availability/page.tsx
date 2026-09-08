'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Calendar, 
  ArrowLeft, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  TrendingUp,
  Save,
  Info
} from 'lucide-react';
import { fetchHostAvailability, updateHostAvailability } from '@/lib/api';
import { AvailabilityRecord } from '@/types';

export default function HostAvailabilityPage() {
  const [records, setRecords] = useState<AvailabilityRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<AvailabilityRecord | null>(null);
  const [priceOverride, setPriceOverride] = useState<string>('');
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchHostAvailability('host-kalim-01', 'hs-kalim-01');
        setRecords(data);
      } catch (err) {
        console.error('Failed to load availability:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleToggle = async (rec: AvailabilityRecord) => {
    const updatedStatus = !rec.is_available;
    try {
      const updated = await updateHostAvailability(
        'host-kalim-01',
        rec.homestay_id,
        rec.date,
        updatedStatus,
        rec.price_override_inr
      );
      setRecords(prev => prev.map(r => r.date === rec.date ? updated : r));
      setSaveStatus(`Date ${rec.date} updated to ${updatedStatus ? 'AVAILABLE' : 'BLOCKED'}`);
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      console.error('Failed to update availability:', err);
    }
  };

  const handlePriceSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRecord) return;
    const priceVal = priceOverride ? parseInt(priceOverride) : undefined;
    try {
      const updated = await updateHostAvailability(
        'host-kalim-01',
        selectedRecord.homestay_id,
        selectedRecord.date,
        selectedRecord.is_available,
        priceVal
      );
      setRecords(prev => prev.map(r => r.date === selectedRecord.date ? updated : r));
      setSelectedRecord(null);
      setPriceOverride('');
      setSaveStatus(`Custom tariff set for ${selectedRecord.date}: ₹${priceVal || 'Standard'}`);
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      console.error('Failed to save price override:', err);
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
              Room Availability & Seasonal Rates
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Manage booking windows for Pineview Orchid Retreat (Kalimpong)
            </p>
          </div>

          {saveStatus && (
            <div className="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{saveStatus}</span>
            </div>
          )}
        </div>

        {/* Informational Banner */}
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-900 dark:text-amber-300 flex items-start gap-2.5">
          <Info className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
          <div>
            <span className="font-bold">Crowd Balance Automation: </span>
            When tourist congestion in Darjeeling peaks (85%+ crowd index), Yatri Setu automatically prioritizes your open calendar dates to incoming travelers, boosting your occupancy without commission hikes.
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-amber-600 mx-auto" />
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
                <Calendar className="w-4 h-4 text-amber-500" />
                <span>Next 30 Days Availability Grid</span>
              </h2>
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1 text-emerald-600 font-semibold">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Available
                </span>
                <span className="flex items-center gap-1 text-slate-400 font-semibold">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Blocked
                </span>
              </div>
            </div>

            {/* 30-Day Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
              {records.map((r) => {
                const dateObj = new Date(r.date);
                const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
                const dayNum = dateObj.getDate();
                const month = dateObj.toLocaleDateString('en-US', { month: 'short' });

                return (
                  <div
                    key={r.date}
                    className={`p-3.5 rounded-2xl border transition-all flex flex-col justify-between gap-2 ${
                      r.is_available
                        ? 'bg-emerald-500/5 dark:bg-emerald-950/20 border-emerald-500/30'
                        : 'bg-slate-100 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700 opacity-70'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold text-slate-400">{dayName}</span>
                        <span className={`w-2 h-2 rounded-full ${r.is_available ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                      </div>
                      <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">
                        {dayNum} {month}
                      </div>
                      {r.price_override_inr ? (
                        <span className="text-[11px] font-bold text-amber-600 block mt-1">
                          ₹{r.price_override_inr}/nt
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400 block mt-1">
                          Standard ₹2,100
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1 pt-2 border-t border-slate-200/60 dark:border-slate-800">
                      <button
                        type="button"
                        onClick={() => handleToggle(r)}
                        className={`flex-1 py-1 rounded text-[10px] font-bold transition-all ${
                          r.is_available
                            ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 hover:bg-rose-200'
                            : 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-200'
                        }`}
                      >
                        {r.is_available ? 'Block' : 'Open'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedRecord(r);
                          setPriceOverride(r.price_override_inr ? String(r.price_override_inr) : '');
                        }}
                        className="px-2 py-1 rounded text-[10px] font-bold bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-300"
                        title="Set Custom Price"
                      >
                        ₹
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Price Override Modal Drawer */}
            {selectedRecord && (
              <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-500/30 text-xs space-y-3">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-slate-900 dark:text-white">
                    Set Custom Tariff for {selectedRecord.date}
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedRecord(null)}
                    className="text-slate-400 hover:text-slate-600 font-bold"
                  >
                    Cancel
                  </button>
                </div>
                <form onSubmit={handlePriceSave} className="flex items-center gap-3">
                  <div className="relative flex-1">
                    <span className="absolute left-3 top-2 text-slate-400 font-bold">₹</span>
                    <input
                      type="number"
                      placeholder="e.g. 2600"
                      value={priceOverride}
                      onChange={(e) => setPriceOverride(e.target.value)}
                      className="w-full pl-7 p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-bold outline-none focus:ring-2 focus:ring-amber-500"
                    />
                  </div>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-amber-600 text-white font-bold text-xs hover:bg-amber-700 flex items-center gap-1"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>Save Tariff</span>
                  </button>
                </form>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
