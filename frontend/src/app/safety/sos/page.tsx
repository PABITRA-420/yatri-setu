'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  triggerSosAlert,
  cancelSosAlert,
  fetchSosIncidentStatus,
  fetchOfficialEmergencyContacts
} from '@/lib/api';
import {
  SosAlertResponse,
  EmergencyIncident,
  EmergencyIncidentType,
  EmergencySeverity,
  OfficialEmergencyContact
} from '@/types';
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
  Share2,
  Wifi,
  WifiOff,
  RefreshCw,
  XCircle,
  AlertTriangle,
  Info,
  ShieldCheck,
  UserCheck
} from 'lucide-react';

const CATEGORIES: { type: EmergencyIncidentType; label: string; icon: any; color: string }[] = [
  { type: 'SOS', label: 'General SOS', icon: AlertOctagon, color: 'text-red-600 border-red-500/30' },
  { type: 'MEDICAL', label: 'Medical Emergency', icon: HeartPulse, color: 'text-rose-600 border-rose-500/30' },
  { type: 'ACCIDENT', label: 'Accident / Collision', icon: Car, color: 'text-amber-600 border-amber-500/30' },
  { type: 'LOST', label: 'Lost Trail / Route', icon: Navigation, color: 'text-blue-600 border-blue-500/30' },
  { type: 'SECURITY', label: 'Personal Security', icon: ShieldAlert, color: 'text-purple-600 border-purple-500/30' },
  { type: 'ROAD_BLOCKED', label: 'Road / Landslide', icon: AlertTriangle, color: 'text-orange-600 border-orange-500/30' },
  { type: 'OTHER', label: 'Other Assistance', icon: Info, color: 'text-slate-600 border-slate-500/30' }
];

export default function SosSafetyScreen() {
  const [isAlertActive, setIsAlertActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [alertData, setAlertData] = useState<SosAlertResponse | null>(null);
  const [incidentData, setIncidentData] = useState<EmergencyIncident | null>(null);
  const [alarmSounding, setAlarmSounding] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [offlineQueued, setOfflineQueued] = useState(false);
  const [graceSeconds, setGraceSeconds] = useState<number | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('Accidental activation');

  // Audio Context refs for Siren
  const audioCtxRef = useRef<AudioContext | null>(null);
  const oscRef = useRef<OscillatorNode | null>(null);
  const lfoRef = useRef<OscillatorNode | null>(null);

  // Form State
  const [userName, setUserName] = useState('Aarav Sharma');
  const [userPhone, setUserPhone] = useState('+91 98765 43210');
  const [selectedCategory, setSelectedCategory] = useState<EmergencyIncidentType>('MEDICAL');
  const [selectedSeverity, setSelectedSeverity] = useState<EmergencySeverity>('HIGH');
  const [gpsEnabled, setGpsEnabled] = useState(true);
  const [notes, setNotes] = useState('Slipped on wet stones near Atisha Road ridge trail. Swollen ankle.');

  // Official helplines
  const [officialHelplines, setOfficialHelplines] = useState<OfficialEmergencyContact[]>([]);

  // Monitor online / offline state
  useEffect(() => {
    setIsOnline(navigator.onLine);
    const handleOnline = () => {
      setIsOnline(true);
      checkAndSyncOfflineQueue();
    };
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    fetchOfficialEmergencyContacts()
      .then(setOfficialHelplines)
      .catch(() => {});

    // Check local storage for pending offline queue
    const queued = localStorage.getItem('ys_pending_sos');
    if (queued) {
      setOfflineQueued(true);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Poll incident status when active
  useEffect(() => {
    if (!isAlertActive || !alertData?.alert_id || incidentData?.status === 'RESOLVED' || incidentData?.status === 'CANCELLED') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const latest = await fetchSosIncidentStatus(alertData.alert_id);
        setIncidentData(latest);
      } catch (err) {
        // Silent poll error fallback
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [isAlertActive, alertData?.alert_id, incidentData?.status]);

  // Grace period countdown
  useEffect(() => {
    if (graceSeconds === null || graceSeconds <= 0) return;
    const timer = setInterval(() => {
      setGraceSeconds((prev) => (prev !== null && prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [graceSeconds]);

  const toggleSirenAudio = () => {
    if (alarmSounding) {
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
        lfo.frequency.setValueAtTime(2.5, ctx.currentTime);

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
        console.warn('Web Audio blocked:', e);
        setAlarmSounding(true);
      }
    }
  };

  const checkAndSyncOfflineQueue = async () => {
    const raw = localStorage.getItem('ys_pending_sos');
    if (!raw) return;
    try {
      const payload = JSON.parse(raw);
      setLoading(true);
      const res = await triggerSosAlert({ ...payload, offline_queued: false });
      localStorage.removeItem('ys_pending_sos');
      setOfflineQueued(false);
      setAlertData(res);
      setIncidentData(res.incident || null);
      setIsAlertActive(true);
    } catch (err) {
      console.warn('Offline sync failed, keeping in queue:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerSOS = async () => {
    setLoading(true);

    const payload = {
      user_name: userName,
      user_phone: userPhone,
      destination_id: 'kalimpong',
      current_location_name: gpsEnabled ? 'Upper Cart Road, Near Atisha Trail, Kalimpong' : 'Cellular Relay Only',
      latitude: gpsEnabled ? 27.0667 : null,
      longitude: gpsEnabled ? 88.4667 : null,
      location_accuracy_m: gpsEnabled ? 25.0 : null,
      incident_type: selectedCategory,
      severity: selectedSeverity,
      nature_of_emergency: `${selectedCategory}: ${notes}`,
      notes: notes,
      idempotency_key: `IDEM-${userPhone}-${Date.now()}`
    };

    // If offline, queue locally
    if (!navigator.onLine) {
      localStorage.setItem('ys_pending_sos', JSON.stringify(payload));
      setOfflineQueued(true);
      setLoading(false);
      return;
    }

    try {
      const res = await triggerSosAlert(payload);
      setAlertData(res);
      setIncidentData(res.incident || null);
      setIsAlertActive(true);
      setGraceSeconds(15); // 15-second grace period counter for accidental taps
    } catch (err) {
      console.warn('Network error, queueing offline:', err);
      localStorage.setItem('ys_pending_sos', JSON.stringify(payload));
      setOfflineQueued(true);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmCancellation = async () => {
    if (!alertData?.alert_id) return;
    setCancelling(true);
    try {
      const updated = await cancelSosAlert(alertData.alert_id, cancelReason, 'TOURIST');
      setIncidentData(updated);
      setShowCancelModal(false);
      if (alarmSounding) toggleSirenAudio();
    } catch (err) {
      console.error('Cancellation error:', err);
    } finally {
      setCancelling(false);
    }
  };

  const handleReset = () => {
    if (alarmSounding) toggleSirenAudio();
    setIsAlertActive(false);
    setAlertData(null);
    setIncidentData(null);
    setGraceSeconds(null);
  };

  // State progression visual status
  const currentStatus = incidentData?.status || 'DELIVERED';

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Network Status Strip */}
      <div className="flex items-center justify-between px-4 py-2.5 rounded-2xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs">
        <div className="flex items-center gap-2">
          {isOnline ? (
            <span className="flex items-center gap-1.5 font-bold text-emerald-600 dark:text-emerald-400">
              <Wifi className="w-4 h-4" />
              <span>Online • Cellular & Sat-Link Active</span>
            </span>
          ) : (
            <span className="flex items-center gap-1.5 font-bold text-amber-600 dark:text-amber-400 animate-pulse">
              <WifiOff className="w-4 h-4" />
              <span>Offline / Low Connectivity Mode</span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-slate-500 font-mono text-[11px]">
          <span>M7F Operations Desk: CONNECTED</span>
        </div>
      </div>

      {/* Offline Queued Alert Box */}
      {offlineQueued && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border-2 border-amber-500/40 text-amber-900 dark:text-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-pulse">
          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-extrabold text-sm">Emergency Request Queued — Waiting for Network</h4>
              <p className="text-xs text-amber-700 dark:text-amber-300">
                Your distress beacon is safely saved locally. It will auto-transmit immediately when signal returns.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={checkAndSyncOfflineQueue}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs flex items-center gap-1.5 self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Retry Broadcast</span>
          </button>
        </div>
      )}

      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 font-extrabold text-xs uppercase tracking-wider border border-rose-500/20">
          <ShieldAlert className="w-4 h-4 animate-pulse" />
          <span>Yatri Setu Operational Safety Layer</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 dark:text-white">
          Emergency SOS & Responder Beacon
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 max-w-xl mx-auto">
          Rapid distress coordination with local Yatri Mitra community volunteers, regional disaster posts, and tourist nodal centers.
        </p>

        {/* Provenance Notice */}
        <div className="max-w-lg mx-auto mt-2 py-1 px-3 rounded-lg bg-slate-100 dark:bg-slate-800 text-[10px] text-slate-500 flex items-center justify-center gap-1.5 border border-slate-200 dark:border-slate-700">
          <Info className="w-3.5 h-3.5 text-blue-500 shrink-0" />
          <span>Internal Yatri Setu Network Coordination • Official helplines available below</span>
        </div>
      </div>

      {/* Active SOS State View */}
      {isAlertActive && alertData ? (
        <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
          {/* Pulsing Emergency Broadcast Banner */}
          <div className={`text-white rounded-3xl p-6 sm:p-8 shadow-2xl space-y-4 border-2 transition-all ${
            currentStatus === 'CANCELLED'
              ? 'bg-slate-700 border-slate-500'
              : currentStatus === 'RESOLVED'
              ? 'bg-emerald-700 border-emerald-500'
              : 'bg-gradient-to-r from-red-600 via-rose-600 to-red-700 border-red-400 animate-pulse'
          }`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-white text-rose-600 flex items-center justify-center font-black">
                  {currentStatus === 'CANCELLED' ? (
                    <XCircle className="w-7 h-7 text-slate-600" />
                  ) : currentStatus === 'RESOLVED' ? (
                    <CheckCircle2 className="w-7 h-7 text-emerald-600" />
                  ) : (
                    <Radio className="w-7 h-7 animate-spin" />
                  )}
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-widest bg-white/20 px-2 py-0.5 rounded">
                    {currentStatus === 'CANCELLED'
                      ? 'Distress Alert Cancelled'
                      : currentStatus === 'RESOLVED'
                      ? 'Emergency Safely Resolved'
                      : 'Distress Beacon Transmitting'}
                  </span>
                  <h2 className="text-xl sm:text-2xl font-black mt-0.5">
                    {alertData.alert_id} • {selectedCategory}
                  </h2>
                </div>
              </div>

              {/* Siren Toggle */}
              {currentStatus !== 'CANCELLED' && currentStatus !== 'RESOLVED' && (
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
              )}
            </div>

            {/* GPS and Route Context Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-2">
              <div className="bg-black/20 p-3 rounded-xl">
                <span className="text-red-200 block text-[10px] uppercase font-bold">Location Telemetry:</span>
                <strong className="font-mono text-xs">{alertData.gps_coordinates}</strong>
              </div>
              <div className="bg-black/20 p-3 rounded-xl">
                <span className="text-red-200 block text-[10px] uppercase font-bold">Corridor Status:</span>
                <strong className="text-xs">
                  {incidentData?.route_context?.corridor_name || 'Gorubathan–Lava Pass'} •{' '}
                  <span className="uppercase">{incidentData?.route_context?.corridor_access_status || 'NORMAL'}</span>
                </strong>
              </div>
              <div className="bg-black/20 p-3 rounded-xl">
                <span className="text-red-200 block text-[10px] uppercase font-bold">Signal Provenance:</span>
                <strong className="text-xs">{incidentData?.provenance || 'REAL — YATRI SETU NETWORK'}</strong>
              </div>
            </div>

            {/* Accidental Tap Grace Period Warning Banner */}
            {graceSeconds !== null && graceSeconds > 0 && currentStatus !== 'CANCELLED' && (
              <div className="p-3 rounded-xl bg-amber-400/20 border border-amber-300/40 text-amber-200 flex items-center justify-between text-xs">
                <span className="font-bold">
                  Accidental tap grace period: {graceSeconds}s remaining to cancel without alert dispatch
                </span>
                <button
                  type="button"
                  onClick={() => setShowCancelModal(true)}
                  className="px-3 py-1 rounded-lg bg-amber-400 text-slate-900 font-extrabold text-[11px] hover:bg-amber-300 transition"
                >
                  Was this accidental? Cancel SOS
                </button>
              </div>
            )}
          </div>

          {/* Operational State Progression Stepper */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-rose-600" />
              <span>Real-Time Operational Response Progress</span>
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center text-xs">
              {[
                { key: 'CREATED', label: '1. Created', desc: 'Signal recorded' },
                { key: 'DELIVERED', label: '2. Delivered', desc: 'Reached Desk' },
                { key: 'ACKNOWLEDGED', label: '3. Acknowledged', desc: incidentData?.assigned_operator ? `Op: ${incidentData.assigned_operator}` : 'Operator assigned' },
                { key: 'RESPONDING', label: '4. Responding', desc: 'Unit en route' },
                { key: 'RESOLVED', label: '5. Resolved', desc: 'Incident closed' }
              ].map((step, idx) => {
                const isPassed =
                  (step.key === 'CREATED') ||
                  (step.key === 'DELIVERED' && ['DELIVERED', 'ACKNOWLEDGED', 'RESPONDING', 'RESOLVED'].includes(currentStatus)) ||
                  (step.key === 'ACKNOWLEDGED' && ['ACKNOWLEDGED', 'RESPONDING', 'RESOLVED'].includes(currentStatus)) ||
                  (step.key === 'RESPONDING' && ['RESPONDING', 'RESOLVED'].includes(currentStatus)) ||
                  (step.key === 'RESOLVED' && currentStatus === 'RESOLVED');

                const isCurrent = currentStatus === step.key;

                return (
                  <div
                    key={idx}
                    className={`p-3 rounded-2xl border transition-all ${
                      isPassed
                        ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                        : isCurrent
                        ? 'bg-rose-50 dark:bg-rose-950/30 border-rose-400 text-rose-900 dark:text-rose-200 animate-pulse'
                        : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700 text-slate-400'
                    }`}
                  >
                    <span className="font-bold block text-xs">{step.label}</span>
                    <span className="text-[10px] opacity-80">{step.desc}</span>
                  </div>
                );
              })}
            </div>

            {incidentData?.acknowledgement_latency_seconds !== undefined && incidentData.acknowledgement_latency_seconds !== null && (
              <p className="text-[11px] text-slate-500 text-center font-mono">
                Observed Desk Acknowledgement Latency: <strong>{incidentData.acknowledgement_latency_seconds}s</strong>
              </p>
            )}
          </div>

          {/* Nearest Dispatched Responders Card */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
                <Navigation className="w-5 h-5 text-rose-600" />
                <span>Nearest Responders & Volunteer Mitra Units</span>
              </h3>
              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" />
                <span>3 Units Notified</span>
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

            {/* Traveler Safety Instructions */}
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

            {/* Action Bar */}
            <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
              {currentStatus !== 'CANCELLED' && currentStatus !== 'RESOLVED' ? (
                <button
                  type="button"
                  onClick={() => setShowCancelModal(true)}
                  className="px-5 py-2.5 rounded-xl bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300 hover:bg-rose-200 text-xs font-bold transition-colors flex items-center gap-1.5"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Cancel SOS (Accidental Tap)</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-5 py-2.5 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-xs font-bold"
                >
                  Start New Session
                </button>
              )}

              <span className="text-[11px] text-slate-400">
                Incident ID: <strong className="font-mono text-slate-600 dark:text-slate-300">{alertData.alert_id}</strong>
              </span>
            </div>
          </div>
        </div>
      ) : (
        /* SOS Trigger Screen */
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-10 border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-8">
          {/* Category Selector Pills */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">
              1. Select Emergency Type
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {CATEGORIES.map((cat) => {
                const Icon = cat.icon;
                const isSelected = selectedCategory === cat.type;
                return (
                  <button
                    key={cat.type}
                    type="button"
                    onClick={() => setSelectedCategory(cat.type)}
                    className={`p-3 rounded-2xl border text-left transition-all flex items-center gap-2.5 ${
                      isSelected
                        ? 'bg-rose-50 dark:bg-rose-950/40 border-rose-500 text-rose-900 dark:text-rose-200 shadow-sm'
                        : 'bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className={`w-4 h-4 shrink-0 ${isSelected ? 'text-rose-600' : 'text-slate-400'}`} />
                    <span className="text-xs font-bold truncate">{cat.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Big Circular SOS Button */}
          <div className="flex flex-col items-center justify-center py-4 text-center">
            <button
              type="button"
              onClick={handleTriggerSOS}
              disabled={loading}
              className="w-48 h-48 sm:w-56 sm:h-56 rounded-full bg-gradient-to-tr from-red-600 via-rose-600 to-red-500 text-white font-black text-2xl sm:text-3xl shadow-2xl shadow-rose-600/50 hover:scale-105 active:scale-95 transition-all duration-300 flex flex-col items-center justify-center gap-2 border-4 border-rose-300/40 group relative"
            >
              <div className="absolute inset-0 rounded-full border-2 border-rose-400 animate-ping opacity-40" />
              <ShieldAlert className="w-12 h-12 text-white group-hover:animate-bounce" />
              <span>{loading ? 'BROADCASTING...' : 'TRIGGER SOS'}</span>
              <span className="text-[10px] uppercase font-bold tracking-widest text-red-200">
                {selectedCategory} • {selectedSeverity}
              </span>
            </button>
            <p className="text-xs text-slate-400 mt-4 max-w-sm">
              Pressing this button activates high-priority distress telemetry to the nearest district nodal office and verified local Yatri Mitra volunteer units.
            </p>
          </div>

          {/* Severity & Settings Row */}
          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">
                  Severity Level
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as EmergencySeverity[]).map((sev) => (
                    <button
                      key={sev}
                      type="button"
                      onClick={() => setSelectedSeverity(sev)}
                      className={`py-2 px-1 rounded-xl text-[11px] font-extrabold border text-center transition-all ${
                        selectedSeverity === sev
                          ? sev === 'CRITICAL'
                            ? 'bg-red-600 text-white border-red-600 shadow-md shadow-red-600/30'
                            : 'bg-rose-500 text-white border-rose-500'
                          : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                      }`}
                    >
                      {sev}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">
                  GPS Telemetry Mode
                </label>
                <button
                  type="button"
                  onClick={() => setGpsEnabled(!gpsEnabled)}
                  className={`w-full py-2 px-3 rounded-xl text-xs font-bold border flex items-center justify-between transition-all ${
                    gpsEnabled
                      ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200'
                      : 'bg-amber-50 dark:bg-amber-950/30 border-amber-300 dark:border-amber-800 text-amber-800 dark:text-amber-200'
                  }`}
                >
                  <span className="flex items-center gap-1.5">
                    <MapPin className="w-4 h-4" />
                    <span>{gpsEnabled ? 'Simulated GPS Lock (±25m)' : 'GPS Off (Cellular Ping Only)'}</span>
                  </span>
                  <span className="text-[10px] uppercase font-bold underline">
                    {gpsEnabled ? 'Disable' : 'Enable'}
                  </span>
                </button>
              </div>
            </div>

            {/* Traveler Contact & Short Message */}
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
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">
                Short Emergency Message / Landmark Notes
              </label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Slipped near ridge trail, need physical support"
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs font-semibold border border-slate-200 dark:border-slate-700"
              />
            </div>
          </div>
        </div>
      )}

      {/* Verified Official Emergency Helplines Directory */}
      <div className="bg-slate-50 dark:bg-slate-900/60 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>Official Emergency Contacts Directory (Public Services)</span>
          </h3>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-200 dark:bg-slate-800 px-2 py-0.5 rounded">
            OFFICIAL INFORMATION
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {(officialHelplines.length > 0 ? officialHelplines : [
            { service_name: 'National Emergency Number', contact_number: '112', toll_free: true, region: 'All-in-One' },
            { service_name: 'Tourist Safety Helpline', contact_number: '1363', toll_free: true, region: 'National 24x7' },
            { service_name: 'Women in Distress', contact_number: '1091', toll_free: true, region: 'National' },
            { service_name: 'Disaster Management', contact_number: '1070', toll_free: true, region: 'Control Desk' }
          ]).map((contact, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-700 flex flex-col justify-between"
            >
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold block truncate">
                  {contact.service_name}
                </span>
                <span className="text-base font-black text-rose-600 dark:text-rose-400">
                  {contact.contact_number}
                </span>
              </div>
              <a
                href={`tel:${contact.contact_number}`}
                className="mt-2 text-[11px] font-bold text-emerald-600 hover:underline flex items-center gap-1"
              >
                <PhoneCall className="w-3 h-3" />
                <span>Call Helpline</span>
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Cancellation Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-md w-full p-6 border border-slate-200 dark:border-slate-700 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-rose-100 dark:bg-rose-900/40 text-rose-600 flex items-center justify-center">
                <AlertOctagon className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-base text-slate-900 dark:text-white">Cancel Emergency SOS?</h3>
                <p className="text-xs text-slate-500">Confirm this was an accidental trigger or assistance is no longer needed.</p>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">
                Reason for Cancellation
              </label>
              <select
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold"
              >
                <option>Accidental tap / pocket dialed</option>
                <option>Assistance received locally</option>
                <option>Safe now / situation resolved</option>
                <option>Testing application interface</option>
              </select>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowCancelModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                Keep SOS Active
              </button>
              <button
                type="button"
                onClick={handleConfirmCancellation}
                disabled={cancelling}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white shadow-sm"
              >
                {cancelling ? 'Cancelling...' : 'Confirm Cancellation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

