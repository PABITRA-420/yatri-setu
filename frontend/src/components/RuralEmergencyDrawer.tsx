'use client';

import React, { useState } from 'react';
import { PhoneCall, ShieldAlert, X, Radio, MapPin, Send } from 'lucide-react';
import { RURAL_EMERGENCY_CONTACTS, OFFLINE_SMS_SOS_TEMPLATE } from '@/lib/ruralCache';

export function RuralEmergencyDrawer() {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopySMS = () => {
    let lat: number | null = null;
    let lng: number | null = null;
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        lat = pos.coords.latitude;
        lng = pos.coords.longitude;
        const msg = OFFLINE_SMS_SOS_TEMPLATE(lat, lng);
        navigator.clipboard.writeText(msg);
        setCopied(true);
        setTimeout(() => setCopied(false), 3000);
      }, () => {
        const msg = OFFLINE_SMS_SOS_TEMPLATE(null, null);
        navigator.clipboard.writeText(msg);
        setCopied(true);
        setTimeout(() => setCopied(false), 3000);
      });
    } else {
      const msg = OFFLINE_SMS_SOS_TEMPLATE(null, null);
      navigator.clipboard.writeText(msg);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    }
  };

  return (
    <>
      {/* Floating Offline Emergency Access Badge */}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-24 left-4 md:bottom-6 md:left-6 z-40 px-3 py-2 bg-gradient-to-r from-red-600/90 to-amber-600/90 hover:from-red-500 hover:to-amber-500 text-white rounded-full shadow-xl shadow-red-900/30 backdrop-blur-md flex items-center gap-2 text-xs font-bold transition-all hover:scale-105 active:scale-95 border border-red-400/40 cursor-pointer"
        aria-label="Open 2G Rural Emergency SOS Directory"
      >
        <Radio className="w-4 h-4 animate-pulse text-amber-200" />
        <span className="hidden sm:inline">2G Rural Helpline</span>
        <span className="sm:hidden">SOS</span>
      </button>

      {/* Drawer Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-full max-w-lg bg-stone-900 border border-stone-800 rounded-t-3xl sm:rounded-3xl shadow-2xl p-5 sm:p-6 overflow-hidden animate-in slide-in-from-bottom duration-250">
            <div className="flex items-center justify-between pb-4 border-b border-stone-800">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-red-500/20 text-red-400">
                  <ShieldAlert className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-sm sm:text-base text-white">
                    Offline Rural Emergency Network
                  </h3>
                  <p className="text-xs text-stone-400">
                    Works offline with zero internet (GSM / SMS Call)
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-full hover:bg-stone-800 text-stone-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Emergency Contacts List */}
            <div className="mt-4 space-y-2.5 max-h-[50vh] overflow-y-auto pr-1">
              {RURAL_EMERGENCY_CONTACTS.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-stone-950/80 border border-stone-800/80 rounded-2xl flex items-center justify-between gap-3 hover:border-amber-500/40 transition"
                >
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 rounded-md bg-stone-800 text-[10px] font-bold uppercase text-amber-400 tracking-wider">
                        {item.type}
                      </span>
                    </div>
                    <p className="font-bold text-xs text-stone-200 mt-1">
                      {item.region}
                    </p>
                  </div>
                  <a
                    href={`tel:${item.phone.replace(/\s+/g, '')}`}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shrink-0 transition"
                  >
                    <PhoneCall className="w-3.5 h-3.5" />
                    <span>{item.phone}</span>
                  </a>
                </div>
              ))}
            </div>

            {/* Offline SMS SOS Dispatch */}
            <div className="mt-5 p-3.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-center justify-between gap-3">
              <div>
                <p className="font-bold text-xs text-amber-300 flex items-center gap-1">
                  <Send className="w-3.5 h-3.5" />
                  <span>2G Offline SMS SOS Trigger</span>
                </p>
                <p className="text-[11px] text-stone-400 mt-0.5">
                  Copy GPS text to broadcast via cellular SMS when internet drops.
                </p>
              </div>
              <button
                type="button"
                onClick={handleCopySMS}
                className="px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-stone-950 rounded-xl text-xs font-extrabold shrink-0 transition"
              >
                {copied ? 'Copied!' : 'Copy SMS'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
