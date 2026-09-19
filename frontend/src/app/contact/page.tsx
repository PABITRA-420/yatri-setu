'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  Mail, 
  Phone, 
  MapPin, 
  Send, 
  CheckCircle2, 
  ShieldAlert, 
  RadioTower, 
  Sparkles, 
  Compass, 
  Clock, 
  Building2, 
  ArrowRight,
  LifeBuoy
} from 'lucide-react';
import { CarouselCoverflow } from '@/components/CarouselCoverflow';
import { Button } from '@/components/animate-ui/components/buttons/button';
import { cn } from '@/lib/utils';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    destination: 'darjeeling',
    category: 'crowd-inquiry',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
    }, 750);
  };

  return (
    <div className="min-h-screen bg-[#ffffe3] text-stone-900 transition-colors pb-24">
      {/* 1. HERO HEADER */}
      <section className="relative pt-14 pb-10 sm:pt-20 sm:pb-16 border-b border-stone-300/70 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-amber-500/10 via-transparent to-transparent pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center space-y-5">
          {/* Status Badges */}
          <div className="flex flex-wrap items-center justify-center gap-3">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-600/10 border border-emerald-600/30 text-emerald-800 text-xs sm:text-sm font-bold font-mono shadow-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
              <span>24/7 Telemetry Dispatch Active</span>
            </div>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-600/10 border border-amber-600/30 text-amber-900 text-xs sm:text-sm font-semibold font-mono shadow-xs">
              <Sparkles className="w-4 h-4 text-amber-600" />
              <span>SIH 2026 Core Helpdesk</span>
            </div>
          </div>

          {/* Title */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-stone-950 leading-[1.08]">
            Connect with <br className="hidden sm:block" />
            <span className="font-editorial italic font-normal text-amber-700">
              Yatri Setu Coordination Desk.
            </span>
          </h1>

          <p className="max-w-3xl mx-auto text-base sm:text-xl text-stone-700 leading-relaxed font-medium">
            Reach our field stations across Darjeeling, Kalimpong, and the Neora Valley corridor. Whether you require live transit advisories, homestay assistance, or emergency safety response, we are here around the clock.
          </p>
        </div>
      </section>

      {/* 2. COVERFLOW CAROUSEL: REGIONAL HUBS SHOWCASE */}
      <section className="py-12 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6 text-center space-y-1">
          <span className="text-xs sm:text-sm font-mono font-bold uppercase tracking-widest text-amber-800">
            Field Operations Network
          </span>
          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-stone-950">
            Regional Coordination Centers &amp; Desks
          </h2>
          <p className="text-sm sm:text-base text-stone-600 max-w-xl mx-auto">
            Swipe through active checkpoints and command units stationed across the Eastern Himalayas.
          </p>
        </div>

        <CarouselCoverflow
          showPagination={true}
          showNavigation={true}
          autoplay={true}
          spaceBetween={32}
        />
      </section>

      {/* 3. CONTACT CHANNELS & INTERACTIVE FORM */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 sm:gap-10 items-start">
          
          {/* Left Column: Direct Helplines & Outpost Addresses */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Emergency SOS Quick Dispatch Callout */}
            <div className="p-7 sm:p-8 rounded-3xl bg-rose-500/10 border-2 border-rose-500/30 shadow-lg relative overflow-hidden space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5 text-rose-700 font-extrabold text-base sm:text-lg">
                  <ShieldAlert className="w-6 h-6 shrink-0 text-rose-600" />
                  <span>Immediate Mountain SOS</span>
                </div>
                <span className="px-3 py-1 rounded-full bg-rose-500/20 text-rose-800 font-mono text-xs font-bold uppercase">
                  Toll Free 24/7
                </span>
              </div>

              {/* Increased font size for callout text */}
              <p className="text-sm sm:text-base text-stone-800 leading-relaxed font-medium">
                In case of critical altitude distress, landslide roadblock, or medical emergencies, trigger one-tap GPS rescue dispatch immediately.
              </p>

              <div className="flex flex-wrap gap-3 pt-1">
                <Button
                  asChild
                  className="bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-sm rounded-xl shadow-md px-5 py-3 h-12 flex items-center gap-2 transition-all transform hover:scale-105"
                >
                  <Link href="/safety/sos">
                    <RadioTower className="w-5 h-5" />
                    <span>Open SOS Console (112)</span>
                  </Link>
                </Button>
                <a
                  href="tel:1363"
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white border border-stone-300 text-sm font-bold text-stone-900 hover:bg-stone-100 transition-colors shadow-xs"
                >
                  <Phone className="w-4 h-4 text-amber-700" />
                  <span>Tourist Helpline 1363</span>
                </a>
              </div>
            </div>

            {/* Communication Detail Cards */}
            <div className="bg-white/95 rounded-3xl p-7 sm:p-8 border border-stone-300/80 shadow-xl space-y-6">
              <h3 className="font-extrabold text-xl sm:text-2xl text-stone-950 tracking-tight">
                Official Directory
              </h3>

              <div className="space-y-4 text-sm sm:text-base">
                {/* Phone */}
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-[#faf9f0] border border-stone-200">
                  <div className="w-11 h-11 rounded-xl bg-amber-500/20 text-amber-800 flex items-center justify-center shrink-0 border border-amber-500/30">
                    <Phone className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-xs font-mono uppercase font-bold text-stone-500 block">Regional Support Line</span>
                    <span className="font-extrabold text-base sm:text-lg text-stone-950 block mt-0.5">+91 (354) 225-4011 / 225-4012</span>
                    <p className="text-xs sm:text-sm text-stone-600 mt-1">Mon - Sat: 8:00 AM – 8:00 PM IST</p>
                  </div>
                </div>

                {/* Email */}
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-[#faf9f0] border border-stone-200">
                  <div className="w-11 h-11 rounded-xl bg-emerald-500/20 text-emerald-800 flex items-center justify-center shrink-0 border border-emerald-500/30">
                    <Mail className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-xs font-mono uppercase font-bold text-stone-500 block">Electronic Enquiries</span>
                    <a href="mailto:support@yatrisetu.gov.in" className="font-extrabold text-base sm:text-lg text-amber-800 hover:underline block mt-0.5">
                      support@yatrisetu.gov.in
                    </a>
                    <span className="text-xs sm:text-sm text-stone-600 block mt-1">For panchayat onboarding: host@yatrisetu.org</span>
                  </div>
                </div>

                {/* HQ Location */}
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-[#faf9f0] border border-stone-200">
                  <div className="w-11 h-11 rounded-xl bg-sky-500/20 text-sky-800 flex items-center justify-center shrink-0 border border-sky-500/30">
                    <MapPin className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-xs font-mono uppercase font-bold text-stone-500 block">Headquarters &amp; Command Center</span>
                    <p className="font-semibold text-sm sm:text-base text-stone-850 leading-relaxed mt-0.5">
                      Eastern Himalayan Flow Operations Center<br />
                      Near Ghoom Transit Interchange, Hill Cart Road,<br />
                      Darjeeling District, West Bengal 734102
                    </p>
                  </div>
                </div>
              </div>

              {/* Guarantees */}
              <div className="pt-3 border-t border-stone-200 flex flex-wrap items-center justify-between gap-2 text-xs sm:text-sm text-stone-600">
                <span className="flex items-center gap-1.5 font-medium">
                  <Clock className="w-4 h-4 text-amber-700" />
                  <span>Average reply under 20 mins</span>
                </span>
                <span className="font-mono text-emerald-700 font-bold">100% Verified Response</span>
              </div>
            </div>
          </div>

          {/* Right Column: Interactive Message Submission Form */}
          <div className="lg:col-span-7">
            <div className="bg-white/95 rounded-3xl p-7 sm:p-10 border border-stone-300/80 shadow-2xl relative space-y-6">
              <div>
                <span className="text-xs sm:text-sm font-mono font-bold uppercase tracking-wider text-amber-800">
                  Dispatch Form
                </span>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-stone-950 mt-1">
                  Send a Message to Our Coordination Team
                </h3>
                <p className="text-sm sm:text-base text-stone-600 mt-1.5 leading-relaxed font-medium">
                  Direct telemetry logs, booking questions, or homestay certification inquiries will be routed to the specific ridge coordinator.
                </p>
              </div>

              {submitted ? (
                <div className="py-12 text-center space-y-4 animate-in fade-in zoom-in duration-300">
                  <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-700 flex items-center justify-center mx-auto border border-emerald-500/30">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h4 className="text-2xl sm:text-3xl font-bold text-stone-950">
                    Transmission Dispatched
                  </h4>
                  <p className="text-sm sm:text-base text-stone-700 max-w-md mx-auto leading-relaxed">
                    Thank you, <strong className="text-stone-950">{formData.name || 'traveler'}</strong>. Your inquiry has been routed to the <strong className="capitalize">{formData.destination}</strong> district coordinator. A ticket reference has been logged.
                  </p>
                  <Button
                    onClick={() => {
                      setSubmitted(false);
                      setFormData({
                        name: '',
                        email: '',
                        phone: '',
                        destination: 'darjeeling',
                        category: 'crowd-inquiry',
                        message: ''
                      });
                    }}
                    className="mt-4 bg-stone-950 text-white font-bold text-sm rounded-xl px-6 py-3 h-11 hover:bg-stone-800 transition-colors cursor-pointer"
                  >
                    Send Another Transmission
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5">
                  {/* Name & Email Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <label htmlFor="contact_name" className="text-sm sm:text-base font-bold text-stone-900 block">
                        Full Name *
                      </label>
                      <input
                        id="contact_name"
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="e.g. Aditi Sharma"
                        className="w-full px-4 py-3.5 rounded-2xl bg-[#faf9f0] border border-stone-300 text-stone-950 text-sm sm:text-base focus:outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20 transition-all font-medium"
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="contact_email" className="text-sm sm:text-base font-bold text-stone-900 block">
                        Email Address *
                      </label>
                      <input
                        id="contact_email"
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        placeholder="aditi@example.com"
                        className="w-full px-4 py-3.5 rounded-2xl bg-[#faf9f0] border border-stone-300 text-stone-950 text-sm sm:text-base focus:outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20 transition-all font-medium"
                      />
                    </div>
                  </div>

                  {/* Phone & Destination Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <label htmlFor="contact_phone" className="text-sm sm:text-base font-bold text-stone-900 block">
                        Contact Phone
                      </label>
                      <input
                        id="contact_phone"
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        placeholder="+91 98765 43210"
                        className="w-full px-4 py-3.5 rounded-2xl bg-[#faf9f0] border border-stone-300 text-stone-950 text-sm sm:text-base focus:outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20 transition-all font-medium"
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="contact_destination" className="text-sm sm:text-base font-bold text-stone-900 block">
                        Target Region / Node
                      </label>
                      <select
                        id="contact_destination"
                        value={formData.destination}
                        onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                        className="w-full px-4 py-3.5 rounded-2xl bg-[#faf9f0] border border-stone-300 text-stone-950 text-sm sm:text-base focus:outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20 transition-all font-medium cursor-pointer"
                      >
                        <option value="darjeeling">Darjeeling Core Corridor</option>
                        <option value="kalimpong">Kalimpong Ridge Sanctuary</option>
                        <option value="lava">Lava &amp; Neora Valley</option>
                        <option value="rishop">Rishop Sunrise Point</option>
                        <option value="lolegaon">Lolegaon Canopy Ridge</option>
                        <option value="mirik">Mirik Lake Valley</option>
                        <option value="all">General / Entire Circuit</option>
                      </select>
                    </div>
                  </div>

                  {/* Inquiry Topic */}
                  <div className="space-y-2">
                    <label htmlFor="contact_category" className="text-sm sm:text-base font-bold text-stone-900 block">
                      Inquiry Category
                    </label>
                    <select
                      id="contact_category"
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-4 py-3.5 rounded-2xl bg-[#faf9f0] border border-stone-300 text-stone-950 text-sm sm:text-base focus:outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20 transition-all font-medium cursor-pointer"
                    >
                      <option value="crowd-inquiry">Crowd Density Diagnostics &amp; Alternative Advice</option>
                      <option value="homestay-verification">Panchayat Homestay Booking &amp; Host Support</option>
                      <option value="passes-permits">Digital Travel Pass &amp; Entry Permits</option>
                      <option value="weather-safety">Mountain Weather Advisories &amp; Trail Closures</option>
                      <option value="partnership">Gram Panchayat / Institutional Collaboration</option>
                    </select>
                  </div>

                  {/* Message Field */}
                  <div className="space-y-2">
                    <label htmlFor="contact_message" className="text-sm sm:text-base font-bold text-stone-900 block">
                      Message / Inquiry Details *
                    </label>
                    <textarea
                      id="contact_message"
                      rows={5}
                      required
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      placeholder="Please share travel dates, group size, or details of assistance required..."
                      className="w-full px-4 py-3.5 rounded-2xl bg-[#faf9f0] border border-stone-300 text-stone-950 text-sm sm:text-base focus:outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20 transition-all font-medium resize-y"
                    />
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full h-14 bg-gradient-to-r from-amber-600 via-amber-700 to-amber-800 hover:from-amber-700 hover:to-amber-900 text-white font-extrabold text-base tracking-wide rounded-2xl shadow-lg shadow-amber-600/25 flex items-center justify-center gap-2.5 cursor-pointer transition-all border border-amber-500/40 transform hover:scale-[1.01]"
                  >
                    {isSubmitting ? (
                      <span>Routing Transmission...</span>
                    ) : (
                      <>
                        <Send className="w-5 h-5" />
                        <span>Dispatch Message to Regional Desk</span>
                      </>
                    )}
                  </Button>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
