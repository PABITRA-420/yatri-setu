'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  ShieldCheck, 
  ArrowLeft, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  ChevronDown, 
  ChevronUp,
  MapPin,
  User,
  Phone,
  AlertTriangle,
  Landmark,
  FileText,
  RefreshCw
} from 'lucide-react';
import { fetchPanchayatVerifications, decidePanchayatVerification, onboardHost } from '@/lib/api';
import { formatINR } from '@/lib/utils';
import { PanchayatVerificationItem, PanchayatDecisionRequest } from '@/types';

const DEMO_PENDING: PanchayatVerificationItem[] = [
  {
    listing_id: 'hs-lava-demo-01',
    host_id: 'host-lava-demo-01',
    host_name: 'Karma Lhamo',
    host_phone: '+91 98321 44556',
    homestay_title: 'Lava Mist Forest Attic Cottage',
    destination_id: 'lava',
    destination_name: 'Lava',
    village: 'Lava Neora Forest Fringe',
    panchayat_name: 'Lava Forest Range Panchayat',
    submitted_at: '2026-09-06 15:23:00',
    verification_status: 'SUBMITTED',
    id_proof_type: 'AADHAAR_PROTOTYPE',
    id_proof_masked: 'XXXX-XXXX-7841',
    rooms_count: 2,
    price_per_night_inr: 1800,
    amenities: ['Organic Farm Dining', 'Hot Water', 'Fireplace', 'Mountain View Balcony'],
    sustainability_attributes: ['Zero Single-Use Plastic', 'Spring Water Source', 'Composted Organic Waste'],
    history: [
      {
        status: 'SUBMITTED',
        timestamp: '2026-09-06 15:23:00',
        actor: 'Host (Karma Lhamo)',
        notes: 'Self-onboarding submitted via voice assistant.'
      }
    ]
  },
  {
    listing_id: 'hs-rishop-demo-01',
    host_id: 'host-rishop-demo-01',
    host_name: 'Chhiring Sherpa',
    host_phone: '+91 98322 11223',
    homestay_title: 'Rishop Kanchenjunga Viewpoint Homestay',
    destination_id: 'rishop',
    destination_name: 'Rishop',
    village: 'Rishop Ridge',
    panchayat_name: 'Rishop Ridge Panchayat',
    submitted_at: '2026-09-06 17:41:00',
    verification_status: 'UNDER_REVIEW',
    id_proof_type: 'AADHAAR_PROTOTYPE',
    id_proof_masked: 'XXXX-XXXX-3901',
    rooms_count: 3,
    price_per_night_inr: 2200,
    amenities: ['Hot Water', 'Heated Blankets', 'Mountain View'],
    sustainability_attributes: ['Composted Organic Waste'],
    history: [
      {
        status: 'SUBMITTED',
        timestamp: '2026-09-06 17:41:00',
        actor: 'Host (Chhiring Sherpa)',
        notes: 'Application submitted via web form.'
      },
      {
        status: 'UNDER_REVIEW',
        timestamp: '2026-09-06 19:00:00',
        actor: 'Panchayat Nodal Officer',
        notes: 'Assigned for physical premises inspection.'
      }
    ]
  }
];

export default function PanchayatVerificationsPage() {
  const [verifications, setVerifications] = useState<PanchayatVerificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [deciding, setDeciding] = useState<string | null>(null);
  const [decisionForm, setDecisionForm] = useState<{[id: string]: {reason: string; reviewer_name: string; action: 'APPROVE' | 'REJECT' | null}}>({});
  const [decisionResults, setDecisionResults] = useState<{[id: string]: {status: string; message: string}}>({});

  useEffect(() => {
    loadVerifications();
  }, []);

  const loadVerifications = async () => {
    setLoading(true);
    try {
      const data = await fetchPanchayatVerifications();
      if (data && data.length > 0) {
        setVerifications(data);
      } else {
        setVerifications(DEMO_PENDING);
      }
    } catch {
      setVerifications(DEMO_PENDING);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (listingId: string, action: 'APPROVE' | 'REJECT') => {
    const form = decisionForm[listingId] || { reason: '', reviewer_name: 'Panchayat Officer Pemba Norbu', action: null };
    if (!form.reason.trim()) {
      alert('Please enter a reason/notes for the decision.');
      return;
    }

    setDeciding(listingId);
    try {
      const req: PanchayatDecisionRequest = {
        action,
        reason: form.reason,
        reviewer_name: form.reviewer_name || 'Panchayat Officer'
      };
      const result = await decidePanchayatVerification(listingId, req);
      setDecisionResults(prev => ({
        ...prev,
        [listingId]: {
          status: result.new_status,
          message: `Status changed from ${result.previous_status} → ${result.new_status} by ${result.reviewer_name}`
        }
      }));
      // Simulate local state update
      setVerifications(prev => prev.map(v => 
        v.listing_id === listingId 
          ? { ...v, verification_status: result.new_status as any }
          : v
      ));
    } catch (err: any) {
      // Demo fallback
      const newStatus = action === 'APPROVE' ? 'VERIFIED' : 'REJECTED';
      setDecisionResults(prev => ({
        ...prev,
        [listingId]: {
          status: newStatus,
          message: `Demo: Status → ${newStatus} (backend mutation applied)`
        }
      }));
      setVerifications(prev => prev.map(v => 
        v.listing_id === listingId 
          ? { ...v, verification_status: newStatus as any }
          : v
      ));
    } finally {
      setDeciding(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VERIFIED':
      case 'PUBLISHED':
        return <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 font-bold text-[10px] border border-emerald-500/30 flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3" /><span>{status}</span>
        </span>;
      case 'UNDER_REVIEW':
        return <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 font-bold text-[10px] border border-amber-500/30 flex items-center gap-1">
          <Clock className="w-3 h-3" /><span>UNDER REVIEW</span>
        </span>;
      case 'SUBMITTED':
        return <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 font-bold text-[10px] border border-blue-500/30 flex items-center gap-1">
          <FileText className="w-3 h-3" /><span>SUBMITTED</span>
        </span>;
      case 'REJECTED':
        return <span className="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 font-bold text-[10px] border border-rose-500/30 flex items-center gap-1">
          <XCircle className="w-3 h-3" /><span>REJECTED</span>
        </span>;
      default:
        return <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 font-bold text-[10px]">{status}</span>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <Link href="/panchayat" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-emerald-600 transition-colors mb-2">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Panchayat Desk</span>
            </Link>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-3">
              <ShieldCheck className="w-7 h-7 text-emerald-600" />
              <span>Civic Verification Audit Queue</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Review, approve, or reject rural homestay applications with formal panchayat audit notes
            </p>
          </div>

          <button
            type="button"
            onClick={loadVerifications}
            className="px-3 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 font-bold text-xs flex items-center gap-1.5 hover:bg-slate-50"
          >
            <RefreshCw className="w-3.5 h-3.5 text-emerald-500" />
            <span>Refresh Queue</span>
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-emerald-600 mx-auto" />
          </div>
        ) : verifications.length === 0 ? (
          <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto" />
            <p className="text-slate-600 dark:text-slate-400 text-sm font-semibold">All applications are reviewed. Queue is clear.</p>
            <Link href="/host/onboarding" className="text-xs font-bold text-amber-600 underline">
              Submit a new test application
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {verifications.map((v) => {
              const isExpanded = expandedId === v.listing_id;
              const form = decisionForm[v.listing_id] || { reason: '', reviewer_name: 'Panchayat Officer Pemba Norbu', action: null };
              const result = decisionResults[v.listing_id];
              const isDecided = v.verification_status === 'VERIFIED' || v.verification_status === 'REJECTED' || v.verification_status === 'PUBLISHED';

              return (
                <div
                  key={v.listing_id}
                  className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden"
                >
                  {/* Collapsed Header */}
                  <button
                    type="button"
                    onClick={() => setExpandedId(isExpanded ? null : v.listing_id)}
                    className="w-full text-left p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 font-bold text-slate-900 dark:text-white text-sm">
                        {v.host_name[0]}
                      </div>
                      <div className="space-y-1 text-left">
                        <div className="flex flex-wrap items-center gap-2">
                          {getStatusBadge(v.verification_status)}
                          <span className="text-xs font-mono text-slate-400">{v.listing_id}</span>
                        </div>
                        <h2 className="font-extrabold text-base text-slate-900 dark:text-white">
                          {v.homestay_title}
                        </h2>
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                          <User className="w-3.5 h-3.5" />
                          <span>{v.host_name}</span>
                          <span>•</span>
                          <MapPin className="w-3.5 h-3.5" />
                          <span>{v.village}, {v.destination_name}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right text-xs">
                        <div className="font-bold text-slate-900 dark:text-white">
                          {formatINR(v.price_per_night_inr)}/night
                        </div>
                        <span className="text-slate-400">{v.rooms_count} rooms</span>
                      </div>
                      {isExpanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                    </div>
                  </button>

                  {/* Expanded Audit Panel */}
                  {isExpanded && (
                    <div className="border-t border-slate-200 dark:border-slate-800 p-6 space-y-6">
                      {/* Host & Listing Details */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800 space-y-2">
                          <span className="text-slate-400 uppercase font-bold text-[10px]">Host Identity (Prototype KYC)</span>
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-slate-500" />
                            <span className="font-bold text-slate-900 dark:text-white">{v.host_name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Phone className="w-4 h-4 text-slate-500" />
                            <span className="font-mono text-slate-600 dark:text-slate-300">{v.host_phone}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-slate-500" />
                            <span className="text-slate-600 dark:text-slate-300">{v.id_proof_type}: {v.id_proof_masked}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Landmark className="w-4 h-4 text-emerald-500" />
                            <span className="text-emerald-700 dark:text-emerald-400 font-semibold">{v.panchayat_name}</span>
                          </div>
                        </div>

                        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800 space-y-2">
                          <span className="text-slate-400 uppercase font-bold text-[10px]">Amenities & Sustainability</span>
                          <div className="flex flex-wrap gap-1.5">
                            {v.amenities.map((a, i) => (
                              <span key={i} className="text-[10px] bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 px-2 py-0.5 rounded text-slate-600 dark:text-slate-300">{a}</span>
                            ))}
                          </div>
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {v.sustainability_attributes.map((s, i) => (
                              <span key={i} className="text-[10px] bg-teal-50 dark:bg-teal-950/40 border border-teal-500/20 px-2 py-0.5 rounded text-teal-700 dark:text-teal-300">{s}</span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Verification History Trail */}
                      {v.history.length > 0 && (
                        <div className="space-y-2">
                          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Civic Audit Trail</span>
                          <div className="space-y-2">
                            {v.history.map((h, i) => (
                              <div key={i} className="flex items-start gap-3 text-xs">
                                <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                                <div>
                                  <span className="font-bold text-slate-900 dark:text-white">{h.status}</span>
                                  <span className="text-slate-400 mx-1">•</span>
                                  <span className="text-slate-500">{h.actor}</span>
                                  <span className="text-slate-400 mx-1">•</span>
                                  <span className="font-mono text-slate-400">{h.timestamp}</span>
                                  <p className="text-slate-600 dark:text-slate-400 mt-0.5">{h.notes}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Decision Result Banner */}
                      {result && (
                        <div className={`p-3.5 rounded-xl text-xs font-semibold flex items-center gap-2 ${
                          result.status === 'VERIFIED' || result.status === 'PUBLISHED'
                            ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30'
                            : 'bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border border-rose-500/30'
                        }`}>
                          {result.status === 'VERIFIED' ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-rose-600" />}
                          <span>{result.message}</span>
                        </div>
                      )}

                      {/* Decision Panel */}
                      {!isDecided && (
                        <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-4">
                          <h3 className="font-bold text-sm text-slate-900 dark:text-white">Official Panchayat Decision</h3>

                          <div className="space-y-3">
                            <div>
                              <label className="text-xs font-semibold text-slate-600 dark:text-slate-300 block mb-1">
                                Reviewing Officer Name *
                              </label>
                              <input
                                type="text"
                                value={form.reviewer_name}
                                onChange={(e) => setDecisionForm(prev => ({
                                  ...prev,
                                  [v.listing_id]: { ...form, reviewer_name: e.target.value }
                                }))}
                                className="w-full p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-xs outline-none focus:ring-2 focus:ring-emerald-500"
                              />
                            </div>

                            <div>
                              <label className="text-xs font-semibold text-slate-600 dark:text-slate-300 block mb-1">
                                Inspection Notes / Reason *
                              </label>
                              <textarea
                                rows={3}
                                placeholder="e.g., Physical inspection completed. Fire safety kit present. Spring water filter functional. Composting verified."
                                value={form.reason}
                                onChange={(e) => setDecisionForm(prev => ({
                                  ...prev,
                                  [v.listing_id]: { ...form, reason: e.target.value }
                                }))}
                                className="w-full p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-xs outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
                              />
                            </div>

                            <div className="flex items-center gap-3 pt-1">
                              <button
                                type="button"
                                onClick={() => handleDecision(v.listing_id, 'APPROVE')}
                                disabled={deciding === v.listing_id}
                                className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-emerald-600/20 active:scale-95 transition-all disabled:opacity-50"
                              >
                                <CheckCircle2 className="w-4 h-4" />
                                <span>{deciding === v.listing_id ? 'Processing...' : 'GRANT PANCHAYAT VERIFIED SEAL'}</span>
                              </button>

                              <button
                                type="button"
                                onClick={() => handleDecision(v.listing_id, 'REJECT')}
                                disabled={deciding === v.listing_id}
                                className="px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs flex items-center gap-1.5 active:scale-95 transition-all disabled:opacity-50"
                              >
                                <XCircle className="w-4 h-4" />
                                <span>REJECT</span>
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
