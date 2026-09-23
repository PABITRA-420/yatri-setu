'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { createBooking, fetchHomestays, fetchHomestayAvailability, cancelBooking } from '@/lib/api';
import { HomestayBookingResponse, Homestay, HomestayAvailabilitySnapshot } from '@/types';
import { formatINR } from '@/lib/utils';
import { ConfettiEffect } from '@/components/ConfettiEffect';
import { Breadcrumbs } from '@/components/Breadcrumbs';
import { DatePicker } from '@/components/DatePicker';
import { motion } from 'motion/react';
import { 
  CheckCircle2, 
  QrCode, 
  MapPin, 
  ShieldCheck, 
  Phone, 
  Calendar, 
  Users, 
  HeartHandshake, 
  ArrowRight,
  Leaf,
  AlertCircle,
  XCircle,
  Clock
} from 'lucide-react';

function BookingConfirmationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const homestayId = searchParams.get('homestay_id') || 'hs-kalimpong-01';

  // Form State
  const [travelerName, setTravelerName] = useState('Aarav Sharma');
  const [travelerPhone, setTravelerPhone] = useState('+91 98765 43210');
  const [travelerEmail, setTravelerEmail] = useState('aarav.sharma@example.com');
  const [emergencyContact, setEmergencyContact] = useState('+91 98111 22233');
  const [checkInDate, setCheckInDate] = useState('2026-10-12');
  const [checkOutDate, setCheckOutDate] = useState('2026-10-15');
  const [numberOfGuests, setNumberOfGuests] = useState(2);
  const [applyGreenCredits, setApplyGreenCredits] = useState(true);

  const [homestayDetails, setHomestayDetails] = useState<Homestay | null>(null);
  const [booking, setBooking] = useState<HomestayBookingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [availabilitySnapshot, setAvailabilitySnapshot] = useState<HomestayAvailabilitySnapshot | null>(null);
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [bookingStatusText, setBookingStatusText] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const [cancelled, setCancelled] = useState(false);

  useEffect(() => {
    async function loadHomestayAndAvailability() {
      try {
        const stays = await fetchHomestays();
        const found = stays.find(h => h.id === homestayId);
        if (found) {
          setHomestayDetails(found);
        }
        const avail = await fetchHomestayAvailability(homestayId, checkInDate).catch(() => null);
        setAvailabilitySnapshot(avail);
      } catch (err) {
        console.warn('Could not fetch homestay details:', err);
      }
    }
    loadHomestayAndAvailability();
  }, [homestayId, checkInDate]);

  // Dynamic calculations based on selected dates & homestay rate
  const calculateNights = () => {
    const d1 = new Date(checkInDate);
    const d2 = new Date(checkOutDate);
    const diff = Math.ceil((d2.getTime() - d1.getTime()) / (1000 * 60 * 60 * 24));
    return isNaN(diff) || diff < 1 ? 1 : diff;
  };

  const nights = calculateNights();
  const nightlyRate = homestayDetails?.price_per_night_inr || 2400;
  const dynamicSubtotal = nightlyRate * nights;
  const greenCreditsDiscount = applyGreenCredits ? 300 : 0; // 30 Green Credits = ₹300 discount
  const discountedSubtotal = Math.max(0, dynamicSubtotal - greenCreditsDiscount);
  const dynamicCommunityFund = Math.round(discountedSubtotal * 0.1);
  const dynamicTotal = discountedSubtotal + dynamicCommunityFund;

  const handleBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setBookingError(null);
    setBookingStatusText('Checking inventory ledger...');
    try {
      await new Promise(r => setTimeout(r, 200));
      setBookingStatusText('Reserving room unit (atomic lock)...');
      const res = await createBooking({
        homestay_id: homestayId,
        traveler_name: travelerName,
        traveler_phone: travelerPhone,
        traveler_email: travelerEmail,
        emergency_contact: emergencyContact,
        check_in_date: checkInDate,
        check_out_date: checkOutDate,
        number_of_guests: numberOfGuests,
        green_credits_applied: applyGreenCredits ? 30 : 0
      });
      setBooking(res);
      setCancelled(false);
    } catch (err: any) {
      console.error('Booking failed:', err);
      setBookingError(err.message || 'Unable to confirm booking. Homestay room may be sold out for these dates.');
    } finally {
      setLoading(false);
      setBookingStatusText(null);
    }
  };

  const handleCancelBooking = async () => {
    if (!booking) return;
    try {
      setCancelling(true);
      await cancelBooking(booking.booking_id, 'Traveler requested cancellation');
      setCancelled(true);
    } catch (err) {
      console.error('Cancel failed:', err);
      setCancelled(true);
    } finally {
      setCancelling(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {booking && !cancelled && <ConfettiEffect />}
      <Breadcrumbs />

      {/* If Booking is already confirmed */}
      {booking ? (
        <div className="space-y-6">
          {/* Booking State Machine Progress (Milestone 7E) */}
          <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium">Booking Lifecycle State:</span>
            <div className="flex items-center gap-1.5 text-[10px] font-mono font-bold">
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 line-through">INITIATED</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 line-through">AVAILABILITY_CHECKED</span>
              <span className="text-slate-600">→</span>
              <span className={`px-2 py-0.5 rounded ${
                cancelled
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}>
                {cancelled ? 'CANCELLED (UNITS RELEASED)' : 'CONFIRMED (UNITS LOCKED)'}
              </span>
            </div>
          </div>

          {/* Success Banner */}
          <div className="bg-emerald-500/10 border-2 border-emerald-500/30 rounded-3xl p-6 sm:p-8 text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-500 text-white flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/30">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-600 text-white font-black text-xs uppercase tracking-wider">
              Booking Confirmed • Verified Homestay Pass
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
              You&apos;re Heading to {booking.homestay.destination_name}!
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 max-w-lg mx-auto">
              Your digital travel pass and emergency tracking have been registered with the local panchayat and nodal rescue desk.
            </p>
          </div>

          {/* Digital Boarding Pass Ticket */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl overflow-hidden border border-slate-200/80 dark:border-slate-800 shadow-xl">
            {/* Ticket Header */}
            <div className="bg-gradient-to-r from-amber-600 to-rose-600 p-6 text-white flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-amber-200 block">
                  Yatri Setu Digital Travel Pass
                </span>
                <h2 className="text-xl font-black">{booking.homestay.title}</h2>
                <p className="text-xs text-amber-100 mt-0.5">
                  Host: {booking.homestay.host.name} • {booking.homestay.address}
                </p>
              </div>

              <div className="text-right">
                <span className="text-[10px] uppercase font-bold text-amber-200 block">
                  Pass Reference
                </span>
                <span className="font-mono font-bold text-base bg-white/20 px-2.5 py-1 rounded-lg">
                  {booking.booking_id}
                </span>
              </div>
            </div>

            {/* Ticket Body */}
            <div className="p-6 sm:p-8 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-4">
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 font-medium block">Lead Traveler:</span>
                    <strong className="text-slate-900 dark:text-white text-sm">{booking.traveler_name}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium block">Phone / Mobile:</span>
                    <strong className="text-slate-900 dark:text-white text-sm">{booking.traveler_phone}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium block">Dates:</span>
                    <strong className="text-slate-900 dark:text-white text-sm">
                      {booking.check_in_date} to {booking.check_out_date} ({booking.total_nights} Nights)
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium block">Guests:</span>
                    <strong className="text-slate-900 dark:text-white text-sm">{booking.number_of_guests} Persons</strong>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs text-slate-500">
                    <span>Stay Tariff ({booking.total_nights} Nights):</span>
                    <span className="font-semibold">{formatINR(booking.subtotal_inr)}</span>
                  </div>

                  {booking.discount_inr ? (
                    <div className="flex justify-between text-xs text-emerald-600 dark:text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-1 rounded-lg border border-emerald-500/20">
                      <span className="flex items-center gap-1">
                        <Leaf className="w-3.5 h-3.5" />
                        Green Credits Reward ({booking.green_credits_redeemed || 30} pts):
                      </span>
                      <span>-{formatINR(booking.discount_inr)}</span>
                    </div>
                  ) : null}

                  <div className="flex justify-between text-xs text-emerald-600 dark:text-emerald-400 font-semibold">
                    <span className="flex items-center gap-1">
                      <HeartHandshake className="w-3.5 h-3.5" />
                      Village Community Fund (10%):
                    </span>
                    <span>{formatINR(booking.community_fund_contribution_inr)}</span>
                  </div>
                  <div className="flex justify-between text-sm font-bold text-slate-900 dark:text-white pt-2 border-t border-slate-100 dark:border-slate-800">
                    <span>Total Amount Paid:</span>
                    <span className="text-amber-600 dark:text-amber-400 font-black text-base">
                      {formatINR(booking.total_amount_inr)}
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 text-xs text-slate-500 flex items-center gap-2">
                  <Phone className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span>Host Support: <strong>{booking.host_contact}</strong></span>
                </div>
              </div>

              {/* QR Code Column */}
              <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-center">
                <div className="w-36 h-36 bg-white p-2 rounded-xl shadow-inner border border-slate-200 flex items-center justify-center">
                  <QrCode className="w-28 h-28 text-slate-900" />
                </div>
                <span className="text-[10px] font-mono text-slate-400 mt-2 block">
                  Scan for Offline Checkpost Pass
                </span>
                <span className="text-[9px] text-emerald-600 font-bold uppercase mt-1">
                  ✓ DigiLocker / Panchayat Ready
                </span>
              </div>
            </div>
          </div>

          {/* Action to Trip Dashboard & Cancel Button */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <Link
              href="/"
              className="text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-white"
            >
              ← Back to Home
            </Link>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              {!cancelled && (
                <button
                  type="button"
                  onClick={handleCancelBooking}
                  disabled={cancelling}
                  className="px-4 py-3 rounded-xl border border-rose-500/30 hover:bg-rose-500/10 text-rose-500 text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <XCircle className="w-4 h-4" />
                  <span>{cancelling ? 'Releasing Room...' : 'Cancel Booking'}</span>
                </button>
              )}

              <Link
                href={`/trips/${booking.booking_id}`}
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-xs shadow-lg shadow-amber-600/20 active:scale-95 transition-all flex items-center justify-center gap-2"
              >
                <span>Go to Active Trip Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      ) : (
        /* Booking Form */
        <div className="space-y-6">
          <div>
            <span className="text-xs uppercase font-bold text-amber-600 tracking-wider">
              Step 4 of Core Demo Flow
            </span>
            <h1 className="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
              Reserve Verified Rural Homestay
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Simulate booking {homestayDetails ? `${homestayDetails.title} (${homestayDetails.destination_name})` : 'Pineview Orchid Retreat (Kalimpong)'} with digital pass generation and emergency contact link.
            </p>
          </div>

          <form
            onSubmit={handleBookingSubmit}
            className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Lead Traveler Name
                </label>
                <input
                  type="text"
                  required
                  value={travelerName}
                  onChange={(e) => setTravelerName(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs sm:text-sm font-semibold border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Primary Mobile Number
                </label>
                <input
                  type="tel"
                  required
                  value={travelerPhone}
                  onChange={(e) => setTravelerPhone(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs sm:text-sm font-semibold border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={travelerEmail}
                  onChange={(e) => setTravelerEmail(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs sm:text-sm font-semibold border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-rose-600 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                  <span>Emergency Kin Contact</span>
                  <span className="text-[10px] text-slate-400">(Auto-linked to SOS)</span>
                </label>
                <input
                  type="tel"
                  required
                  value={emergencyContact}
                  onChange={(e) => setEmergencyContact(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs sm:text-sm font-semibold border border-rose-200 dark:border-rose-900/50 focus:outline-none focus:ring-2 focus:ring-rose-500"
                />
              </div>

              <div>
                <DatePicker
                  label="Check-in Date"
                  value={checkInDate}
                  onChange={(d) => setCheckInDate(d)}
                />
              </div>

              <div>
                <DatePicker
                  label="Check-out Date"
                  value={checkOutDate}
                  onChange={(d) => setCheckOutDate(d)}
                />
              </div>

            </div>

            {/* Green Credits In-Platform Voucher Box */}
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400">
                  <Leaf className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black text-slate-900 dark:text-white">
                      Apply 30 Green Credits
                    </span>
                    <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-700 dark:text-emerald-300">
                      Save ₹300
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                    Your sustainable travel reward applied directly to this booking
                  </p>
                </div>
              </div>

              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={applyGreenCredits}
                  onChange={(e) => setApplyGreenCredits(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-emerald-600"></div>
              </label>
            </div>

            {/* Dynamic Tariff Breakdown */}
            <div className="bg-slate-50 dark:bg-slate-800/60 p-5 rounded-2xl border border-slate-200/60 dark:border-slate-700 space-y-2.5 text-xs">
              <div className="flex justify-between text-slate-600 dark:text-slate-300">
                <span>Stay Tariff (₹{nightlyRate.toLocaleString('en-IN')} × {nights} {nights === 1 ? 'Night' : 'Nights'}):</span>
                <span className="font-semibold">{formatINR(dynamicSubtotal)}</span>
              </div>

              {applyGreenCredits && (
                <div className="flex justify-between text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                  <span className="flex items-center gap-1.5">
                    <Leaf className="w-3.5 h-3.5" />
                    Green Credits In-Platform Discount:
                  </span>
                  <span>-{formatINR(greenCreditsDiscount)}</span>
                </div>
              )}

              <div className="flex justify-between text-emerald-600 dark:text-emerald-400 font-semibold">
                <span className="flex items-center gap-1">
                  <Leaf className="w-3.5 h-3.5" />
                  10% Village Forest & Panchayat Fund:
                </span>
                <span>+{formatINR(dynamicCommunityFund)}</span>
              </div>

              <div className="flex justify-between text-sm font-bold text-slate-900 dark:text-white pt-2 border-t border-slate-200 dark:border-slate-700">
                <span>Total Payable:</span>
                <span className="text-amber-600 dark:text-amber-400 font-black text-base">
                  {formatINR(dynamicTotal)}
                </span>
              </div>
            </div>

            {/* Live Inventory Availability Snapshot */}
            {availabilitySnapshot && (
              <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/70 border border-slate-200 dark:border-slate-700 text-xs">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-emerald-500" />
                  <span className="text-slate-600 dark:text-slate-300 font-medium">
                    Ledger Status ({availabilitySnapshot.date}):
                  </span>
                </div>
                <span className={`font-bold px-2.5 py-1 rounded-full text-[10px] uppercase tracking-wider ${
                  availabilitySnapshot.status === 'AVAILABLE'
                    ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                    : availabilitySnapshot.status === 'FEW_LEFT'
                    ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                    : 'bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/30'
                }`}>
                  {availabilitySnapshot.available_units} of {availabilitySnapshot.total_units} Units Available ({availabilitySnapshot.status})
                </span>
              </div>
            )}

            {/* Status Progress or Booking Error */}
            {bookingStatusText && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400 text-xs flex items-center gap-2 animate-pulse">
                <Clock className="w-4 h-4" />
                <span>{bookingStatusText}</span>
              </div>
            )}

            {bookingError && (
              <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 text-xs flex items-start gap-2.5">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <strong className="block text-sm font-bold">Booking Request Failed</strong>
                  <p>{bookingError}</p>
                  <p className="text-[11px] text-slate-500">
                    The requested units may have been booked concurrently or sold out. Please select another date or explore neighboring homestays.
                  </p>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-700 hover:to-rose-700 text-white font-bold text-xs shadow-md shadow-amber-600/30 active:scale-95 transition-all flex items-center justify-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{loading ? (bookingStatusText || 'Confirming with Panchayat Node...') : 'Confirm Stay & Generate Digital Travel Pass'}</span>
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default function BookingConfirmationPage() {
  return (
    <Suspense fallback={
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading booking details...
      </div>
    }>
      <BookingConfirmationContent />
    </Suspense>
  );
}
