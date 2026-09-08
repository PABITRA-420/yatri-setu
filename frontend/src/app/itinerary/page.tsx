'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { generateItinerary, optimizeItinerary } from '@/lib/api';
import { ItineraryResponse, ItineraryOptimizeRequest } from '@/types';
import { ItineraryTimeline } from '@/components/ItineraryTimeline';
import { formatINR } from '@/lib/utils';
import { 
  Sparkles, 
  Calendar, 
  Clock, 
  Users, 
  DollarSign, 
  Compass, 
  ArrowRight, 
  CheckCircle2, 
  Home, 
  Flame,
  Leaf,
  CloudRain,
  Sun,
  ShieldCheck,
  Send,
  RefreshCw,
  TrendingDown,
  Info,
  Trees,
  Landmark,
  Umbrella,
  Baby,
  Eye
} from 'lucide-react';

function ItineraryPlannerContent() {
  const searchParams = useSearchParams();
  const initialDest = searchParams.get('destination') || 'kalimpong';

  const [destinationId, setDestinationId] = useState(initialDest);
  const [durationDays, setDurationDays] = useState(3);
  const [travelerType, setTravelerType] = useState('Couple');
  const [pace, setPace] = useState('Moderate');
  const [selectedInterests, setSelectedInterests] = useState<string[]>([
    'Nature',
    'Culture',
    'Local Food'
  ]);
  const [budgetLevel, setBudgetLevel] = useState('Moderate');

  const [itinerary, setItinerary] = useState<ItineraryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');
  const [activeDirective, setActiveDirective] = useState<string | null>(null);

  const interestOptions = [
    'Nature',
    'Culture',
    'Local Food',
    'Photography',
    'Meditation',
    'Orchid Gardening',
    'Trekking'
  ];

  const handleInterestToggle = (interest: string) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter((i) => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const res = await generateItinerary({
        destination_id: destinationId,
        duration_days: durationDays,
        traveler_type: travelerType,
        pace,
        interests: selectedInterests,
        budget_level: budgetLevel
      });
      setItinerary(res);
      setActiveDirective(null);
    } catch (err) {
      console.error('Failed to generate itinerary:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async (instruction: string, customInstruction?: string) => {
    if (!itinerary) return;
    setOptimizing(true);
    setActiveDirective(instruction);
    try {
      const payload: ItineraryOptimizeRequest = {
        itinerary_id: itinerary.itinerary_id,
        destination_id: itinerary.destination_id,
        instruction,
        custom_instruction: customInstruction,
        current_itinerary: itinerary
      };
      const res = await optimizeItinerary(payload);
      setItinerary(res);
      if (customInstruction) setCustomPrompt('');
    } catch (err) {
      console.error('Failed to optimize itinerary:', err);
    } finally {
      setOptimizing(false);
    }
  };

  // Initial load auto-generates for quick demo readiness
  useEffect(() => {
    handleGenerate();
  }, [destinationId]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header & AI Badge */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>SIH 2026 • Tourist Flow & Adaptive AI Engine</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Adaptive AI Travel Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 max-w-2xl mt-1">
            Genuinely adaptive multi-day planning powered by provider abstraction. Guardrails keep crowd scores, pricing, availability, and traveler safety strictly deterministic.
          </p>
        </div>

        {/* AI Provider Status Pill */}
        <div className="bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-2xl p-3.5 flex items-center gap-3 shrink-0 shadow-sm">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
          <div className="text-xs">
            <div className="font-extrabold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <span>AI Provider:</span>
              <span className="text-amber-600 dark:text-amber-400 uppercase font-mono tracking-wide">
                {itinerary?.ai_provider_used || 'MOCK (ZERO-CONFIG)'}
              </span>
            </div>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">
              Deterministic crowd & safety guardrails
            </span>
          </div>
        </div>
      </div>

      {/* Preferences Form Card */}
      <form
        onSubmit={handleGenerate}
        className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Destination Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              Destination
            </label>
            <select
              value={destinationId}
              onChange={(e) => setDestinationId(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs sm:text-sm font-semibold border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              <option value="kalimpong">Kalimpong (Orchid Ridge • 42/100)</option>
              <option value="lava">Lava (Misty Neora Pine • 24/100 • 🌧️ Rain Test)</option>
              <option value="rishop">Rishop (360° Kanchenjunga • 15/100)</option>
              <option value="lolegaon">Lolegaon (Canopy Forest • 18/100)</option>
              <option value="mirik">Mirik (Sumendu Lake • 38/100)</option>
              <option value="darjeeling">Darjeeling (High Demand • 88/100)</option>
            </select>
          </div>

          {/* Duration Days */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              Duration (Days)
            </label>
            <div className="flex items-center gap-2">
              {[1, 2, 3, 4, 5].map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDurationDays(d)}
                  className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
                    durationDays === d
                      ? 'bg-amber-600 text-white shadow-sm'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
                  }`}
                >
                  {d}D
                </button>
              ))}
            </div>
          </div>

          {/* Traveler Type */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              Party Type
            </label>
            <select
              value={travelerType}
              onChange={(e) => setTravelerType(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs sm:text-sm font-semibold border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              <option value="Solo">Solo Explorer</option>
              <option value="Couple">Couple / Partners</option>
              <option value="Family">Family with Children</option>
              <option value="Friends">Friends Group</option>
            </select>
          </div>

          {/* Travel Pace */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              Exploration Pace
            </label>
            <div className="flex items-center gap-2">
              {['Relaxed', 'Moderate', 'Active'].map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPace(p)}
                  className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
                    pace === p
                      ? 'bg-amber-600 text-white shadow-sm'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Interests Selector */}
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
            Selected Experiences & Interests
          </label>
          <div className="flex flex-wrap gap-2">
            {interestOptions.map((interest) => {
              const isSelected = selectedInterests.includes(interest);
              return (
                <button
                  key={interest}
                  type="button"
                  onClick={() => handleInterestToggle(interest)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    isSelected
                      ? 'bg-amber-500/20 text-amber-700 dark:text-amber-400 border border-amber-500/40'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-transparent hover:bg-slate-200'
                  }`}
                >
                  {isSelected && '✓ '}
                  {interest}
                </button>
              );
            })}
          </div>
        </div>

        {/* Submit Bar */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3">
          <span className="text-xs text-slate-400">
            Real-time Himalayan weather profile & community impact integrated automatically
          </span>
          <button
            type="submit"
            disabled={loading || optimizing}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-xs shadow-md shadow-amber-600/30 active:scale-95 transition-all flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>{loading ? 'Consulting Travel Intelligence...' : 'Generate Adaptive Itinerary'}</span>
          </button>
        </div>
      </form>

      {/* Itinerary Results Presentation */}
      {itinerary && (
        <div className="space-y-6">
          {/* Summary Badges Banner */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-3 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-extrabold tracking-wider uppercase">
                  {itinerary.crowd_avoidance_rating}
                </span>
                <span className="text-xs text-slate-400">
                  • {itinerary.duration_days} Days Plan
                </span>
                {itinerary.sustainability_score && (
                  <span className="px-3 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/30 text-xs font-extrabold">
                    🌱 Eco Rating: {itinerary.sustainability_score}/100 ({itinerary.sustainability_classification})
                  </span>
                )}
              </div>
              <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
                {itinerary.duration_days}-Day Adaptive Plan: {itinerary.destination_name}
              </h2>
              <p className="text-xs text-slate-300 flex items-center gap-1.5">
                <Leaf className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{itinerary.local_economic_impact_tag}</span>
              </p>
            </div>

            {/* Estimated Total Budget */}
            <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/10 text-center min-w-[200px]">
              <span className="text-[10px] uppercase font-bold text-slate-300 block mb-1">
                Estimated Total Spend
              </span>
              <span className="text-2xl font-black text-amber-400">
                {formatINR(itinerary.total_estimated_budget_inr)}
              </span>
              <span className="text-[10px] text-slate-300 block mt-0.5">
                Excl. homestay stay
              </span>
            </div>
          </div>

          {/* Weather Intelligence Card */}
          {itinerary.weather_forecast && (
            <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200/60 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-xl ${itinerary.weather_forecast.rain_expected ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400' : 'bg-amber-500/10 text-amber-600 dark:text-amber-400'}`}>
                    {itinerary.weather_forecast.rain_expected ? <CloudRain className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-extrabold text-slate-400 tracking-wider">
                      Himalayan Weather Profile • {itinerary.weather_forecast.destination_name}
                    </span>
                    <h4 className="text-sm font-black text-slate-900 dark:text-white">
                      {itinerary.weather_forecast.condition} ({itinerary.weather_forecast.temperature_range_c})
                    </h4>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <div className="px-3 py-1 rounded-xl bg-slate-100 dark:bg-slate-800 text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                    <Eye className="w-3.5 h-3.5 text-indigo-500" />
                    <span>Peak Visibility: {itinerary.weather_forecast.mountain_visibility_score}/100</span>
                  </div>
                  <div className="px-3 py-1 rounded-xl bg-slate-100 dark:bg-slate-800 text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-amber-500" />
                    <span>Best Outdoors: {itinerary.weather_forecast.best_hours_for_outdoors}</span>
                  </div>
                </div>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300">
                <span className="font-bold">Advisory: </span>{itinerary.weather_forecast.advisory}
              </p>

              {/* Weather Adaptation Alert Banner */}
              {itinerary.weather_adaptation_notice && (
                <div className="p-3.5 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/50 flex items-start gap-3 text-xs text-blue-900 dark:text-blue-200">
                  <CloudRain className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-extrabold block mb-0.5">Automated Weather-Defensive Scheduling Active</span>
                    <span>{itinerary.weather_adaptation_notice}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* "Why This Itinerary?" AI Strategic Reasoning Drawer */}
          {itinerary.why_this_itinerary && itinerary.why_this_itinerary.length > 0 && (
            <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-bold text-xs uppercase tracking-wider">
                <Info className="w-4 h-4" />
                <span>Why Yatri Setu Recommended This Plan</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                {itinerary.why_this_itinerary.map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-2.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Sustainability & Tourism Impact Scorecard */}
          {itinerary.tourism_impact && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                    <Leaf className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-black text-slate-900 dark:text-white">
                      Village Sustainability & Economic Impact Scorecard
                    </h3>
                    <span className="text-[11px] text-slate-500">
                      Deterministic verification: spending stays inside the Himalayan Panchayat ecosystem
                    </span>
                  </div>
                </div>
                <div className="text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/30">
                  Rating: {itinerary.sustainability_score}/100 ({itinerary.sustainability_classification})
                </div>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                    Direct Village Retention
                  </span>
                  <div className="text-lg font-black text-slate-900 dark:text-white">
                    {formatINR(itinerary.tourism_impact.estimated_local_spend_inr)}
                  </div>
                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">
                    {itinerary.tourism_impact.direct_village_economy_percent}% kept hyperlocally
                  </span>
                </div>

                <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                    Indigenous Livelihoods
                  </span>
                  <div className="text-lg font-black text-slate-900 dark:text-white">
                    {itinerary.tourism_impact.local_businesses_supported} Partners
                  </div>
                  <span className="text-[10px] text-slate-500">
                    Guides, eateries & weavers
                  </span>
                </div>

                <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                    Gram Panchayat Eco-Fund
                  </span>
                  <div className="text-lg font-black text-slate-900 dark:text-white">
                    {formatINR(itinerary.tourism_impact.community_fund_contribution_inr)}
                  </div>
                  <span className="text-[10px] text-slate-500">
                    2% community reserve
                  </span>
                </div>

                <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                    Carbon Footprint Saved
                  </span>
                  <div className="text-lg font-black text-teal-600 dark:text-teal-400">
                    {itinerary.tourism_impact.carbon_saved_vs_private_car_kg} kg CO₂
                  </div>
                  <span className="text-[10px] text-slate-500">
                    vs private chartered cab
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Interactive "Adapt Itinerary with AI" Directives Bar */}
          <div className="bg-gradient-to-br from-amber-500/10 via-rose-500/5 to-slate-900/5 dark:from-slate-900 dark:to-slate-950 rounded-2xl p-6 border-2 border-amber-500/30 shadow-md space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <h3 className="font-black text-base text-slate-900 dark:text-white">
                  Change My Trip with AI (SIH Adaptive Directives)
                </h3>
              </div>
              {optimizing && (
                <div className="flex items-center gap-2 text-xs font-bold text-amber-600 dark:text-amber-400">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>AI is adapting itinerary...</span>
                </div>
              )}
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-300">
              Click any SIH adaptive directive or type custom travel requirements below. The AI resequences the trip while keeping deterministic safety and pricing intact.
            </p>

            {/* Directive Chips */}
            <div className="flex flex-wrap gap-2 pt-1">
              <button
                type="button"
                disabled={optimizing}
                onClick={() => handleOptimize('MAKE_CHEAPER')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
                  activeDirective === 'MAKE_CHEAPER'
                    ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-amber-400'
                }`}
              >
                <DollarSign className="w-3.5 h-3.5 text-emerald-500" />
                <span>Make it Cheaper (-35%)</span>
              </button>

              <button
                type="button"
                disabled={optimizing}
                onClick={() => handleOptimize('MORE_RELAXED')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
                  activeDirective === 'MORE_RELAXED'
                    ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-amber-400'
                }`}
              >
                <Clock className="w-3.5 h-3.5 text-amber-500" />
                <span>More Relaxed Pace</span>
              </button>

              <button
                type="button"
                disabled={optimizing}
                onClick={() => handleOptimize('MORE_NATURE')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
                  activeDirective === 'MORE_NATURE'
                    ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-amber-400'
                }`}
              >
                <Trees className="w-3.5 h-3.5 text-emerald-600" />
                <span>More Nature & Forests</span>
              </button>

              <button
                type="button"
                disabled={optimizing}
                onClick={() => handleOptimize('MORE_CULTURE')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
                  activeDirective === 'MORE_CULTURE'
                    ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-amber-400'
                }`}
              >
                <Landmark className="w-3.5 h-3.5 text-indigo-500" />
                <span>More Culture & Monasteries</span>
              </button>

              <button
                type="button"
                disabled={optimizing}
                onClick={() => handleOptimize('RAIN_SAFE')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
                  activeDirective === 'RAIN_SAFE'
                    ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-amber-400'
                }`}
              >
                <Umbrella className="w-3.5 h-3.5 text-blue-500" />
                <span>Rain-Safe / Covered</span>
              </button>

              <button
                type="button"
                disabled={optimizing}
                onClick={() => handleOptimize('AVOID_CROWDS')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
                  activeDirective === 'AVOID_CROWDS'
                    ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-amber-400'
                }`}
              >
                <TrendingDown className="w-3.5 h-3.5 text-rose-500" />
                <span>Dawn Anti-Crowd Slot</span>
              </button>

              <button
                type="button"
                disabled={optimizing}
                onClick={() => handleOptimize('FAMILY_FRIENDLY')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
                  activeDirective === 'FAMILY_FRIENDLY'
                    ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-amber-400'
                }`}
              >
                <Baby className="w-3.5 h-3.5 text-orange-500" />
                <span>Family Friendly</span>
              </button>
            </div>

            {/* Free-Text Prompt Input */}
            <div className="flex gap-2 pt-2">
              <input
                type="text"
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Or type custom prompt: e.g. Add an early morning birdwatching hike and local cheese tasting..."
                className="flex-1 px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 text-slate-900 dark:text-white"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && customPrompt.trim()) {
                    handleOptimize('CUSTOM', customPrompt.trim());
                  }
                }}
              />
              <button
                type="button"
                disabled={optimizing || !customPrompt.trim()}
                onClick={() => handleOptimize('CUSTOM', customPrompt.trim())}
                className="px-5 py-2.5 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-bold text-xs rounded-xl transition-all flex items-center gap-1.5 shrink-0 shadow-sm"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Ask AI</span>
              </button>
            </div>

            {/* Optimization History Trail */}
            {itinerary.optimization_history && itinerary.optimization_history.length > 0 && (
              <div className="pt-2 flex items-center gap-2 text-[11px] text-slate-500 overflow-x-auto">
                <span className="font-bold shrink-0">Adaptation Trail:</span>
                {itinerary.optimization_history.map((step, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded-md bg-white/80 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700 text-[10px] whitespace-nowrap"
                  >
                    {step}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Interactive Day-by-Day Timeline */}
          <ItineraryTimeline days={itinerary.days} />

          {/* Next Step in SIH Demo Flow: Select Homestay */}
          <div className="bg-amber-500/10 border-2 border-amber-500/30 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="font-extrabold text-base text-slate-900 dark:text-white">
                Next Step in Demo: Choose a Verified {itinerary.destination_name} Homestay
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-1">
                Stay with verified local host families. 10% of every booking goes directly to the Gram Panchayat village eco-fund.
              </p>
            </div>

            <Link
              href={`/homestays?destination_id=${destinationId}`}
              className="px-6 py-3 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-md shadow-amber-600/20 active:scale-95 transition-all flex items-center gap-2 whitespace-nowrap"
            >
              <Home className="w-4 h-4" />
              <span>Select Verified Homestay</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ItineraryPlannerPage() {
  return (
    <Suspense fallback={
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading adaptive itinerary engine...
      </div>
    }>
      <ItineraryPlannerContent />
    </Suspense>
  );
}
