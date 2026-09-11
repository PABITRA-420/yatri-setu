'use client';

import React, { useState } from 'react';
import { triggerSosAlert } from '@/lib/api';
import { SosAlertResponse } from '@/types';
import { 
  ShieldAlert, 
  Radio, 
  MapPin, 
  PhoneCall, 
  AlertOctagon, 
  Volume2, 
  VolumeX, 
  CheckCircle2, 
  Clock, 
  Car, 
  HeartPulse,
  Navigation,
  Share2
} from 'lucide-react';

export default function SosSafetyScreen() {
  const [isAlertActive, setIsAlertActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [alertData, setAlertData] = useState<SosAlertResponse | null>(null);
  const [alarmSounding, setAlarmSounding] = useState(false);
  const audioCtxRef = React.useRef<AudioContext | null>(null);
  const oscRef = React.useRef<OscillatorNode | null>(null);
  const lfoRef = React.useRef<OscillatorNode | null>(null);

  // Form State
  const [userName, setUserName] = useState('Aarav Sharma');
  const [userPhone, setUserPhone] = useState('+91 98765 43210');
  const [emergencyType, setEmergencyType] = useState('Medical Assistance / Trail Sprain');
  const [notes, setNotes] = useState('Slipped near Atisha Road ridge trail. Need localized physical support.');

  const toggleSirenAudio = () => {
    if (alarmSounding) {
      // Stop siren
      try {
        oscRef.current?.stop();
        lfoRef.current?.stop();
        audioCtxRef.current?.close();
      } catch (e) {
        console.error(e);
      }
      audioCtxRef.current = null;
      setAlarmSounding(false);
    } else {
      // Start real Web Audio siren
      try {
        const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        const ctx = new AudioCtx();
        audioCtxRef.current = ctx;

        const osc = ctx.createOscillator();
        const lfo = ctx.createOscillator();
        const gain = ctx.createGain();
        const lfoGain = ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(650, ctx.currentTime);

        lfo.type = 'sine';
        lfo.frequency.setValueAtTime(2.5, ctx.currentTime); // 2.5 Hz siren wail

        lfoGain.gain.setValueAtTime(250, ctx.currentTime);
        lfo.connect(lfoGain);
        lfoGain.connect(osc.frequency);

        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start();
        lfo.start();

        oscRef.current = osc;
        lfoRef.current = lfo;
        setAlarmSounding(true);
      } catch (e) {
        console.warn('Web Audio not supported or blocked:', e);
        setAlarmSounding(true);
      }
    }
  };

  const handleTriggerSOS = async () => {
    setLoading(true);
    const res = await triggerSosAlert({
      user_name: userName,
      user_phone: userPhone,
      destination_id: 'kalimpong',
      current_location_name: 'Upper Cart Road, Near Atisha Trail, Kalimpong',
      latitude: 27.0667,
      longitude: 88.4667,
      nature_of_emergency: emergencyType
    });
    setAlertData(res);
    setIsAlertActive(true);
    setLoading(false);
  };

  const handleCancelSOS = () => {
    if (alarmSounding) {
      try {
        oscRef.current?.stop();
        lfoRef.current?.stop();
        audioCtxRef.current?.close();
      } catch (e) {
        console.error(e);
      }
    }
    setIsAlertActive(false);
    setAlarmSounding(false);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 font-extrabold text-xs uppercase tracking-wider border border-rose-500/20">
          <ShieldAlert className="w-4 h-4 animate-pulse" />
          <span>SIH 2026 Built-In Traveler Safety Hub</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 dark:text-white">
          Emergency SOS & Responder Beacon
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 max-w-xl mx-auto">
          One-tap distress signal with real-time GPS coordinate relay to local police, medical units, and the verified Yatri Mitra rural volunteer network.
        </p>
      </div>

      {/* Active SOS State View */}
      {isAlertActive && alertData ? (
        <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
          {/* Pulsing Red Emergency Broadcast Banner */}
          <div className="bg-gradient-to-r from-red-600 via-rose-600 to-red-700 text-white rounded-3xl p-6 sm:p-8 shadow-2xl space-y-4 border-2 border-red-400 animate-pulse">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-white text-rose-600 flex items-center justify-center font-black">
                  <Radio className="w-7 h-7 animate-spin" />
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-widest bg-white/20 px-2 py-0.5 rounded">
                    Distress Signal Transmitted
                  </span>
                  <h2 className="text-xl sm:text-2xl font-black mt-0.5">
                    SOS Broadcast Live • {alertData.alert_id}
                  </h2>
                </div>
              </div>

              {/* Siren Toggle */}
              <button
                type="button"
                onClick={toggleSirenAudio}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                  alarmSounding ? 'bg-amber-400 text-slate-900 shadow-lg' : 'bg-white/20 hover:bg-white/30 text-white'
                }`}
              >
                {alarmSounding ? <Volume2 className="w-4 h-4 animate-bounce" /> : <VolumeX className="w-4 h-4" />}
                <span>{alarmSounding ? 'Loud Siren Active' : 'Sound Alarm Siren'}</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-2">
              <div className="bg-black/20 p-3 rounded-xl">
                <span className="text-red-200 block text-[10px] uppercase font-bold">Transmitted GPS Coordinates:</span>
                <strong className="font-mono text-sm">{alertData.gps_coordinates}</strong>
              </div>
              <div className="bg-black/20 p-3 rounded-xl">
                <span className="text-red-200 block text-[10px] uppercase font-bold">Signal Relay Strength:</span>
                <strong className="text-sm">{alertData.beacon_signal_strength}</strong>
              </div>
            </div>
          </div>

          {/* Nearest Dispatched Responders Card */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
                <Navigation className="w-5 h-5 text-rose-600" />
                <span>Nearest Responders Dispatched</span>
              </h3>
              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" />
                <span>3 Units Responding</span>
              </span>
            </div>

            <div className="space-y-3">
              {alertData.nearest_responders.map((responder, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                        {responder.name}
                      </h4>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-600">
                        {responder.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500">
                      {responder.agency} • ~{responder.distance_km} km away
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">
                        Estimated Arrival
                      </span>
                      <span className="font-black text-emerald-600 text-sm">
                        {responder.eta_minutes} Minutes
                      </span>
                    </div>

                    <a
                      href={`tel:${responder.phone}`}
                      className="p-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm flex items-center justify-center transition-colors"
                      title="Direct Call"
                    >
                      <PhoneCall className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>

            {/* Traveler Safety Directives */}
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 text-xs text-slate-700 dark:text-slate-300 space-y-2">
              <span className="font-bold text-amber-700 dark:text-amber-400 block uppercase tracking-wider text-[11px]">
                Traveler Emergency Instructions:
              </span>
              <ul className="space-y-1">
                {alertData.instructions_for_traveler.map((ins, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-amber-600 font-bold">•</span>
                    <span>{ins}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Cancel SOS Button */}
            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={handleCancelSOS}
                className="px-6 py-2.5 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-300 text-xs font-bold transition-colors"
              >
                Stand Down / End Simulated Emergency
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* SOS Trigger Screen */
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-10 border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-8">
          {/* Big Circular SOS Button */}
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <button
              type="button"
              onClick={handleTriggerSOS}
              disabled={loading}
              className="w-48 h-48 sm:w-56 sm:h-56 rounded-full bg-gradient-to-tr from-red-600 via-rose-600 to-red-500 text-white font-black text-2xl sm:text-3xl shadow-2xl shadow-rose-600/50 hover:scale-105 active:scale-95 transition-all duration-300 flex flex-col items-center justify-center gap-2 border-4 border-rose-300/40 group relative"
            >
              <div className="absolute inset-0 rounded-full border-2 border-rose-400 animate-ping opacity-40" />
              <ShieldAlert className="w-12 h-12 text-white group-hover:animate-bounce" />
              <span>{loading ? 'BROADCASTING...' : 'HOLD SOS'}</span>
              <span className="text-[10px] uppercase font-bold tracking-widest text-red-200">
                Click to Trigger Demo
              </span>
            </button>
            <p className="text-xs text-slate-400 mt-4 max-w-sm">
              Pressing this button will transmit high-priority distress telemetry to the nearest district nodal office.
            </p>
          </div>

          {/* Form Parameters for Demo */}
          <div className="pt-6 border-t border-slate-100 dark:border-slate-800 space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">
              Current Traveler Telemetry & Settings
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">
                  Traveler Name
                </label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs font-semibold border border-slate-200 dark:border-slate-700"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">
                  Verified Contact
                </label>
                <input
                  type="text"
                  value={userPhone}
                  onChange={(e) => setUserPhone(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs font-semibold border border-slate-200 dark:border-slate-700"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">
                  Emergency Nature
                </label>
                <select
                  value={emergencyType}
                  onChange={(e) => setEmergencyType(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs font-semibold border border-slate-200 dark:border-slate-700"
                >
                  <option>Medical Assistance / Trail Sprain</option>
                  <option>Route Lost in Forest Canopy</option>
                  <option>Severe Weather Isolation</option>
                  <option>Vehicular Breakdown</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">
                  Simulated GPS Lock
                </label>
                <div className="px-3 py-2 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs font-mono text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                  <span>27.0667° N, 88.4667° E</span>
                  <span className="text-[10px] text-emerald-600 font-bold">Lock: 100%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* National Helplines Directory */}
      <div className="bg-slate-50 dark:bg-slate-900/60 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800">
        <h3 className="font-bold text-sm text-slate-900 dark:text-white mb-3">
          National & State Tourist Safety Helplines
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          {[
            { name: 'National Emergency', num: '112' },
            { name: 'Tourist Safety Desk', num: '1363' },
            { name: 'Women Helpline', num: '1091' },
            { name: 'Disaster Control', num: '1070' },
          ].map((h) => (
            <div key={h.name} className="bg-white dark:bg-slate-800 p-3 rounded-xl border border-slate-200/60 dark:border-slate-700">
              <span className="text-[10px] text-slate-400 font-bold uppercase block">{h.name}</span>
              <span className="text-base font-black text-rose-600 dark:text-rose-400">{h.num}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
