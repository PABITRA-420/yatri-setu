'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Mic, 
  Sparkles, 
  ShieldCheck, 
  Home, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  ArrowLeft,
  Upload,
  Lock,
  Leaf,
  Info,
  Layers,
  FileCheck
} from 'lucide-react';
import { parseVoiceListingDraft, onboardHost } from '@/lib/api';
import { HostOnboardingRequest } from '@/types';

export default function HostOnboardingPage() {
  const router = useRouter();

  // Voice assistant state
  const [spokenText, setSpokenText] = useState(
    'We have a two-room pine wood cottage near Lava Neora Forest fringe. We provide homemade Nepali food, solar hot water, and cardamom trail walks.'
  );
  const [isParsingVoice, setIsParsingVoice] = useState(false);
  const [voiceParsedAlert, setVoiceParsedAlert] = useState<string | null>(null);

  // Form step state
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionSuccess, setSubmissionSuccess] = useState<any | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Form Fields
  const [formData, setFormData] = useState<HostOnboardingRequest>({
    name: 'Karma Lhamo',
    phone: '+91 98321 44556',
    email: 'karma.lhamo@yatrisetu.org',
    village: 'Lava Neora Forest Fringe',
    panchayat_name: 'Lava Forest Range Panchayat',
    destination_id: 'lava',
    languages: ['English', 'Nepali', 'Lepcha'],
    bio: 'Organic cardamom farmer and traditional cook hosting travelers on our family homestead.',
    homestay_title: 'Lava Mist Forest Attic Cottage',
    tagline: 'Wake up to mountain birdcalls at the Neora valley forest edge',
    address: 'Algarah Road, Lava, Kalimpong District - 734319',
    room_type: 'Pine Wood Attic',
    rooms_count: 2,
    max_guests: 4,
    price_per_night_inr: 1800,
    amenities: ['Organic Farm Dining', 'Hot Water', 'Fireplace / Wood Stove', 'Mountain View Balcony'],
    sustainability_attributes: ['Zero Single-Use Plastic', 'Spring Water Source', 'Composted Organic Waste'],
    special_activity: 'Cardamom curing workshop & birding forest walk'
  });

  const samplePrompts = [
    'We have a two-room pine wood cottage near Lava Neora Forest fringe. We provide homemade Nepali food, solar hot water, and cardamom trail walks.',
    'I have 3 traditional rooms in Kalimpong with orchid garden views. We offer organic cheese making and hot butter tea.',
    'Quiet homestay in Rishop with unobstructed Kanchenjunga sunrise views. 2 wooden rooms, farm dining and zero single-use plastic.'
  ];

  const handleVoiceParse = async () => {
    if (!spokenText.trim()) return;
    setIsParsingVoice(true);
    setVoiceParsedAlert(null);
    try {
      const draft = await parseVoiceListingDraft(spokenText);
      setFormData(prev => ({
        ...prev,
        homestay_title: draft.suggested_title || prev.homestay_title,
        tagline: draft.suggested_tagline || prev.tagline,
        destination_id: draft.detected_destination_id || prev.destination_id,
        village: draft.detected_village || prev.village,
        room_type: draft.detected_room_type || prev.room_type,
        rooms_count: draft.suggested_rooms_count || prev.rooms_count,
        amenities: Array.from(new Set([...prev.amenities, ...draft.detected_amenities])),
        sustainability_attributes: Array.from(new Set([...prev.sustainability_attributes, ...draft.detected_sustainability_attributes])),
        special_activity: draft.suggested_experiences[0] || prev.special_activity
      }));
      setVoiceParsedAlert(
        `AI Draft Created! Structured room type (${draft.detected_room_type}), ${draft.detected_amenities.length} amenities, and village location. Guardrail active: Pricing & KYC kept for manual confirmation.`
      );
    } catch (err: any) {
      setVoiceParsedAlert('Failed to parse voice draft. Please enter details manually.');
    } finally {
      setIsParsingVoice(false);
    }
  };

  const handleAmenityToggle = (amenity: string) => {
    setFormData(prev => {
      const exists = prev.amenities.includes(amenity);
      return {
        ...prev,
        amenities: exists ? prev.amenities.filter(a => a !== amenity) : [...prev.amenities, amenity]
      };
    });
  };

  const handleSustainabilityToggle = (attr: string) => {
    setFormData(prev => {
      const exists = prev.sustainability_attributes.includes(attr);
      return {
        ...prev,
        sustainability_attributes: exists
          ? prev.sustainability_attributes.filter(a => a !== attr)
          : [...prev.sustainability_attributes, attr]
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const res = await onboardHost(formData);
      setSubmissionSuccess(res);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error submitting onboarding details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const availableAmenities = [
    'Organic Farm Dining',
    'Hot Water',
    'Solar Water Heating',
    'Fireplace / Wood Stove',
    'Mountain View Balcony',
    'High-Speed Wi-Fi',
    'Home Library & Games',
    'Orchid Nursery Access'
  ];

  const availableSustainability = [
    'Zero Single-Use Plastic',
    'Spring Water Source',
    'Rainwater Harvesting System',
    'Composted Organic Waste',
    'Solar Energy Powered',
    'Locally Sourced Organic Food'
  ];

  if (submissionSuccess) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-16 px-4">
        <div className="max-w-2xl mx-auto bg-white dark:bg-slate-900 rounded-3xl p-8 sm:p-12 border border-slate-200 dark:border-slate-800 shadow-xl text-center space-y-6">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto border border-amber-500/20">
            <FileCheck className="w-8 h-8" />
          </div>

          <div className="space-y-2">
            <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-700 dark:text-amber-400 font-bold text-xs uppercase tracking-wider">
              Status: SUBMITTED
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
              Homestay Application Submitted!
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto">
              Your listing has entered the Gram Panchayat civic review queue. A local nodal officer will inspect safety and hygiene standards.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-left space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Listing ID:</span>
              <span className="font-mono font-bold text-slate-900 dark:text-white">{submissionSuccess.listing?.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Homestay Title:</span>
              <span className="font-bold text-slate-900 dark:text-white">{submissionSuccess.listing?.title}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Local Panchayat:</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">{submissionSuccess.host?.panchayat_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Host Net Share:</span>
              <span className="font-bold text-amber-600">90% of all future bookings</span>
            </div>
          </div>

          <div className="pt-4 flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/host/dashboard"
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-sm shadow-md"
            >
              Go to Host Dashboard
            </Link>
            <Link
              href="/panchayat/verifications"
              className="px-6 py-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-sm hover:bg-slate-200"
            >
              Inspect as Panchayat Officer
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <Link href="/host" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-amber-600 transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Host Overview</span>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
            Rural Homestay Onboarding & Voice Assistant
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Easily list your village cottage with voice assistance, keep 90% income, and get certified by your Gram Panchayat.
          </p>
        </div>

        {/* SECTION 1: VOICE LISTING ASSISTANT (Hackathon Showcase) */}
        <div className="rounded-3xl bg-gradient-to-br from-amber-500/10 via-rose-500/5 to-emerald-500/10 border border-amber-500/30 p-6 sm:p-8 space-y-4 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-amber-500 text-white shadow-md shadow-amber-500/30">
                <Mic className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2">
                  <span>Voice-Assisted Listing Assistant</span>
                  <span className="text-[10px] bg-amber-500/20 text-amber-700 dark:text-amber-400 px-2 py-0.5 rounded-full font-bold uppercase">
                    SIH AI Prototype
                  </span>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Speak naturally about your home or test with sample transcripts. AI parses structure without guessing prices.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <textarea
              value={spokenText}
              onChange={(e) => setSpokenText(e.target.value)}
              rows={3}
              placeholder="Speak or type: 'We have a two-room wooden cottage near Lava Neora Forest. We serve homemade food...'"
              className="w-full p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 outline-none resize-none"
            />

            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap gap-1.5 items-center">
                <span className="text-[11px] text-slate-500 font-medium">Try speaking sample:</span>
                {samplePrompts.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setSpokenText(p)}
                    className="text-[11px] bg-white/80 dark:bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-amber-400"
                  >
                    Sample {idx + 1}
                  </button>
                ))}
              </div>

              <button
                type="button"
                onClick={handleVoiceParse}
                disabled={isParsingVoice || !spokenText.trim()}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-xs shadow-md shadow-amber-600/20 flex items-center gap-2 active:scale-95 transition-all disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isParsingVoice ? 'Structuring Voice Draft...' : 'Convert Voice to Structured Form'}</span>
              </button>
            </div>
          </div>

          {voiceParsedAlert && (
            <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-800 dark:text-emerald-300 flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600" />
              <div>
                <p className="font-semibold">{voiceParsedAlert}</p>
                <p className="text-[10px] text-emerald-600/80 mt-0.5">
                  Review the pre-filled fields below before submitting for official Gram Panchayat verification.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* STEP PROGRESS BAR */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
          <button
            type="button"
            onClick={() => setCurrentStep(1)}
            className={`flex items-center gap-2 text-xs font-bold ${
              currentStep === 1 ? 'text-amber-600' : 'text-slate-400'
            }`}
          >
            <span className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">1</span>
            <span>Host Identity</span>
          </button>
          <div className="flex-1 h-0.5 bg-slate-200 dark:bg-slate-800 mx-2" />
          <button
            type="button"
            onClick={() => setCurrentStep(2)}
            className={`flex items-center gap-2 text-xs font-bold ${
              currentStep === 2 ? 'text-amber-600' : 'text-slate-400'
            }`}
          >
            <span className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">2</span>
            <span>Homestay & Rooms</span>
          </button>
          <div className="flex-1 h-0.5 bg-slate-200 dark:bg-slate-800 mx-2" />
          <button
            type="button"
            onClick={() => setCurrentStep(3)}
            className={`flex items-center gap-2 text-xs font-bold ${
              currentStep === 3 ? 'text-amber-600' : 'text-slate-400'
            }`}
          >
            <span className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">3</span>
            <span>Amenities & Eco</span>
          </button>
          <div className="flex-1 h-0.5 bg-slate-200 dark:bg-slate-800 mx-2" />
          <button
            type="button"
            onClick={() => setCurrentStep(4)}
            className={`flex items-center gap-2 text-xs font-bold ${
              currentStep === 4 ? 'text-amber-600' : 'text-slate-400'
            }`}
          >
            <span className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">4</span>
            <span>Review & Submit</span>
          </button>
        </div>

        {/* MAIN FORM */}
        <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
          {/* STEP 1: HOST DETAILS */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>1. Personal & Panchayat Identity</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Phone Number (for booking alerts) *
                  </label>
                  <input
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Gram Panchayat *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.panchayat_name}
                    onChange={(e) => setFormData({ ...formData, panchayat_name: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Village / Hamlet *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.village}
                    onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                  Host Bio & Heritage Story
                </label>
                <textarea
                  rows={2}
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="flex justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setCurrentStep(2)}
                  className="px-6 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs flex items-center gap-2"
                >
                  <span>Next: Homestay Details</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: HOMESTAY & PRICING */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>2. Homestay Details & Fair Pricing</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Homestay Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.homestay_title}
                    onChange={(e) => setFormData({ ...formData, homestay_title: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Short Tagline *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.tagline}
                    onChange={(e) => setFormData({ ...formData, tagline: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Destination Region *
                  </label>
                  <select
                    value={formData.destination_id}
                    onChange={(e) => setFormData({ ...formData, destination_id: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  >
                    <option value="lava">Lava (Fringe & Pine Forest)</option>
                    <option value="lolegaon">Lolegaon (Heritage Canopy)</option>
                    <option value="rishop">Rishop (Panoramic Ridge)</option>
                    <option value="kalimpong">Kalimpong (Orchid Valleys)</option>
                    <option value="mirik">Mirik (Lake & Orange Orchards)</option>
                    <option value="darjeeling">Darjeeling (Rural Outskirts)</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Room Type *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.room_type}
                    onChange={(e) => setFormData({ ...formData, room_type: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Number of Guest Rooms *
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={formData.rooms_count}
                    onChange={(e) => setFormData({ ...formData, rooms_count: parseInt(e.target.value) || 1 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Price per Night (₹ INR) *
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-slate-400 font-bold">₹</span>
                    <input
                      type="number"
                      required
                      min={500}
                      max={15000}
                      value={formData.price_per_night_inr}
                      onChange={(e) => setFormData({ ...formData, price_per_night_inr: parseInt(e.target.value) || 1000 })}
                      className="w-full pl-8 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-bold text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-amber-500"
                    />
                  </div>
                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400 mt-1 block">
                    You keep ₹{(formData.price_per_night_inr * 0.9).toFixed(0)}/night (90% net). ₹{(formData.price_per_night_inr * 0.05).toFixed(0)} goes to Gram Panchayat fund.
                  </span>
                </div>
              </div>

              <div className="flex justify-between pt-4">
                <button
                  type="button"
                  onClick={() => setCurrentStep(1)}
                  className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold"
                >
                  Previous
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentStep(3)}
                  className="px-6 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs flex items-center gap-2"
                >
                  <span>Next: Amenities & Eco</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: AMENITIES & SUSTAINABILITY */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="space-y-3">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">3. Amenities & Eco-Practices</h2>
                <p className="text-xs text-slate-500">Select standard amenities provided to travelers:</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {availableAmenities.map((amenity) => {
                    const isSelected = formData.amenities.includes(amenity);
                    return (
                      <button
                        type="button"
                        key={amenity}
                        onClick={() => handleAmenityToggle(amenity)}
                        className={`p-2.5 rounded-xl text-left text-xs font-semibold border transition-all ${
                          isSelected
                            ? 'bg-amber-500/10 border-amber-500 text-amber-700 dark:text-amber-400'
                            : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'
                        }`}
                      >
                        {amenity}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-3 pt-2">
                <h3 className="text-sm font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                  <Leaf className="w-4 h-4" />
                  <span>Sustainability Badges (Earns Sustainable Stay Badge)</span>
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {availableSustainability.map((attr) => {
                    const isSelected = formData.sustainability_attributes.includes(attr);
                    return (
                      <button
                        type="button"
                        key={attr}
                        onClick={() => handleSustainabilityToggle(attr)}
                        className={`p-2.5 rounded-xl text-left text-xs font-semibold border transition-all flex items-center justify-between ${
                          isSelected
                            ? 'bg-teal-500/10 border-teal-500 text-teal-700 dark:text-teal-300'
                            : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'
                        }`}
                      >
                        <span>{attr}</span>
                        {isSelected && <CheckCircle2 className="w-4 h-4 text-teal-600" />}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                  Special Local Experience Offered with Stay
                </label>
                <input
                  type="text"
                  value={formData.special_activity}
                  onChange={(e) => setFormData({ ...formData, special_activity: e.target.value })}
                  placeholder="e.g., Organic cardamom curing & forest birding walk"
                  className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="flex justify-between pt-4">
                <button
                  type="button"
                  onClick={() => setCurrentStep(2)}
                  className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold"
                >
                  Previous
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentStep(4)}
                  className="px-6 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs flex items-center gap-2"
                >
                  <span>Next: Review & Submit</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: REVIEW & VERIFICATION SUBMISSION */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                4. Review & Gram Panchayat Verification Submission
              </h2>

              <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-500/20 text-xs text-amber-900 dark:text-amber-200 space-y-2">
                <div className="flex items-center gap-1.5 font-bold">
                  <ShieldCheck className="w-4 h-4 text-amber-600" />
                  <span>Gram Panchayat Verification Protocol</span>
                </div>
                <p>
                  Upon submission, your listing is assigned status <span className="font-mono font-bold bg-amber-200/50 dark:bg-amber-800/40 px-1 py-0.5 rounded">SUBMITTED</span>.
                  The designated village panchayat nodal officer conducts physical and fire safety checks before granting the official <span className="text-emerald-600 dark:text-emerald-400 font-bold">PANCHAYAT VERIFIED</span> seal.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800 space-y-1.5">
                  <span className="text-slate-400 uppercase font-bold text-[10px]">Host Details</span>
                  <p className="font-bold text-slate-900 dark:text-white">{formData.name}</p>
                  <p className="text-slate-600 dark:text-slate-400">{formData.phone} • {formData.email}</p>
                  <p className="text-emerald-600 font-semibold">{formData.panchayat_name}</p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800 space-y-1.5">
                  <span className="text-slate-400 uppercase font-bold text-[10px]">Pricing & Financials</span>
                  <p className="font-bold text-slate-900 dark:text-white">₹{formData.price_per_night_inr} / night</p>
                  <p className="text-slate-600 dark:text-slate-400">Host Net: ₹{(formData.price_per_night_inr * 0.9).toFixed(0)} (90%)</p>
                  <p className="text-teal-600 font-semibold">Community Fund: ₹{(formData.price_per_night_inr * 0.05).toFixed(0)} (5%)</p>
                </div>
              </div>

              {errorMessage && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-500/30 text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errorMessage}</span>
                </div>
              )}

              <div className="flex justify-between pt-4">
                <button
                  type="button"
                  onClick={() => setCurrentStep(3)}
                  className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold"
                >
                  Previous
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-8 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white font-bold text-sm shadow-md shadow-emerald-600/20 active:scale-95 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{isSubmitting ? 'Submitting to Panchayat...' : 'Submit for Panchayat Verification'}</span>
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
