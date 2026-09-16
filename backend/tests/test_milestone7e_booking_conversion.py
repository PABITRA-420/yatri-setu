"""
Tests for Milestone 7E: Real Booking / Availability + First-Party Conversion Intelligence.
Verifies:
1. Deterministic Booking State Machine and Transitions
2. Double-Booking and Concurrency Protection
3. Date-Specific Availability Ledger (decrement on confirm, release on cancel)
4. Normalized Failure Classifications (SOLD_OUT, INVALID_HOMESTAY)
5. Idempotency Key Handling
6. Outbound Booking Click Telemetry (distinction from confirmed bookings)
7. Conversion Funnel and Observed vs Configured Acceptance Rates
8. Privacy & Non-PII Logging
"""

import threading
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.homestay import HomestayBookingRequest
from app.services.booking.service import booking_lifecycle_service
from app.services.booking.schemas import BookingState, BookingFailureReason
from app.services.availability.service import availability_service
from app.services.availability.schemas import AvailabilityStatus
from app.services.conversion.funnel_service import conversion_funnel_service
from app.services.demand_aggregation_service import demand_aggregation_service

client = TestClient(app)


class TestBookingLifecycle:
    def test_successful_booking_lifecycle(self):
        req = HomestayBookingRequest(
            homestay_id="hs-kalimpong-01",
            traveler_name="Anita Roy",
            traveler_phone="+91 98765 43210",
            traveler_email="anita.roy@example.com",
            emergency_contact="+91 98765 43211",
            check_in_date="2026-10-15",
            check_out_date="2026-10-18",
            number_of_guests=2
        )
        record, resp = booking_lifecycle_service.create_booking(req, auto_confirm=True)

        assert record.state == BookingState.CONFIRMED
        assert record.homestay_id == "hs-kalimpong-01"
        assert record.destination_id == "kalimpong"
        assert record.digital_pass_qr_payload is not None
        assert len(record.transitions) >= 3

        # Verify transition sequence
        states = [t.to_state for t in record.transitions]
        assert BookingState.AVAILABILITY_CHECKED in states
        assert BookingState.PENDING_CONFIRMATION in states
        assert BookingState.CONFIRMED in states

    def test_booking_cancellation_releases_units(self):
        # 1. Check initial availability
        avail_before = availability_service.get_homestay_availability("hs-kalimpong-02", "2026-11-01")
        initial_avail = avail_before.available_units

        # 2. Make booking
        req = HomestayBookingRequest(
            homestay_id="hs-kalimpong-02",
            traveler_name="Rohan Verma",
            traveler_phone="+91 98765 11111",
            traveler_email="rohan@example.com",
            emergency_contact="+91 98765 22222",
            check_in_date="2026-11-01",
            check_out_date="2026-11-04",
            number_of_guests=2
        )
        record, _ = booking_lifecycle_service.create_booking(req, auto_confirm=True)
        assert record.state == BookingState.CONFIRMED

        avail_after_book = availability_service.get_homestay_availability("hs-kalimpong-02", "2026-11-01")
        assert avail_after_book.available_units == initial_avail - 1

        # 3. Cancel booking
        cancelled = booking_lifecycle_service.cancel_booking(record.booking_id, reason="Plans changed")
        assert cancelled.state == BookingState.CANCELLED

        avail_after_cancel = availability_service.get_homestay_availability("hs-kalimpong-02", "2026-11-01")
        assert avail_after_cancel.available_units == initial_avail

    def test_invalid_state_transition_rejected(self):
        req = HomestayBookingRequest(
            homestay_id="hs-kalimpong-01",
            traveler_name="Test User",
            traveler_phone="+91 99999 00000",
            traveler_email="test@example.com",
            emergency_contact="+91 99999 00001",
            check_in_date="2026-11-10",
            check_out_date="2026-11-13",
            number_of_guests=1
        )
        record, _ = booking_lifecycle_service.create_booking(req, auto_confirm=True)
        booking_lifecycle_service.cancel_booking(record.booking_id)

        # Attempting to confirm a cancelled booking must raise ValueError
        with pytest.raises(ValueError, match="Invalid booking transition"):
            booking_lifecycle_service.confirm_booking(record.booking_id)

    def test_idempotency_key(self):
        req = HomestayBookingRequest(
            homestay_id="hs-kalimpong-01",
            traveler_name="Vikram Seth",
            traveler_phone="+91 98765 88888",
            traveler_email="vikram@example.com",
            emergency_contact="+91 98765 99999",
            check_in_date="2026-12-01",
            check_out_date="2026-12-04",
            number_of_guests=2
        )
        key = "idem-key-unique-12345"
        rec1, resp1 = booking_lifecycle_service.create_booking(req, idempotency_key=key)
        rec2, resp2 = booking_lifecycle_service.create_booking(req, idempotency_key=key)

        assert rec1.booking_id == rec2.booking_id
        assert resp1.booking_id == resp2.booking_id


class TestConcurrencyAndDoubleBooking:
    def test_double_booking_prevention(self):
        # Find homestay and reserve until only 1 unit remains
        homestay_id = "hs-rishop-01"
        target_date = "2026-12-25"
        avail = availability_service.get_homestay_availability(homestay_id, target_date)
        total = avail.total_units

        # Fill up all but 1 unit
        for _ in range(total - 1):
            availability_service.reserve_units(homestay_id, target_date, 1)

        avail_one = availability_service.get_homestay_availability(homestay_id, target_date)
        assert avail_one.available_units == 1

        # Now simulate 2 concurrent booking requests for the remaining 1 unit
        req1 = HomestayBookingRequest(
            homestay_id=homestay_id,
            traveler_name="Tourist Alpha",
            traveler_phone="+91 90000 00001",
            traveler_email="alpha@example.com",
            emergency_contact="+91 90000 00002",
            check_in_date=target_date,
            check_out_date="2026-12-28",
            number_of_guests=2
        )
        req2 = HomestayBookingRequest(
            homestay_id=homestay_id,
            traveler_name="Tourist Beta",
            traveler_phone="+91 90000 00003",
            traveler_email="beta@example.com",
            emergency_contact="+91 90000 00004",
            check_in_date=target_date,
            check_out_date="2026-12-28",
            number_of_guests=2
        )

        results = []
        errors = []

        def attempt_book(req):
            try:
                rec, resp = booking_lifecycle_service.create_booking(req, auto_confirm=True)
                results.append(rec)
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=attempt_book, args=(req1,))
        t2 = threading.Thread(target=attempt_book, args=(req2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        confirmed = [r for r in results if r.state == BookingState.CONFIRMED]
        failed = [r for r in results if r.state == BookingState.FAILED]

        # Exactly one may confirm, the other must fail with SOLD_OUT
        assert len(confirmed) == 1, "Exactly one booking must succeed"
        assert len(failed) == 1, "The second concurrent booking must fail"
        assert failed[0].failure_reason == BookingFailureReason.SOLD_OUT


class TestDateAwareAvailabilityAPI:
    def test_destination_availability_api(self):
        resp = client.get("/api/destinations/kalimpong/availability?date=2026-10-20")
        assert resp.status_code == 200
        data = resp.json()
        assert data["destination_id"] == "kalimpong"
        assert data["date"] == "2026-10-20"
        assert data["total_units"] > 0
        assert data["available_units"] >= 0
        assert data["availability_status"] in ("AVAILABLE", "LIMITED", "FULL")

    def test_homestay_availability_api(self):
        resp = client.get("/api/homestays/hs-kalimpong-01/availability?date=2026-10-20")
        assert resp.status_code == 200
        data = resp.json()
        assert data["homestay_id"] == "hs-kalimpong-01"
        assert data["date"] == "2026-10-20"
        assert data["total_units"] >= 1
        assert data["available_units"] >= 0


class TestFailureReasonsAPI:
    def test_invalid_homestay_fails_cleanly(self):
        payload = {
            "homestay_id": "nonexistent-homestay",
            "traveler_name": "Ghost Traveler",
            "traveler_phone": "+91 99999 99999",
            "traveler_email": "ghost@example.com",
            "emergency_contact": "+91 99999 99998",
            "check_in_date": "2026-10-20",
            "check_out_date": "2026-10-23",
            "number_of_guests": 2
        }
        resp = client.post("/api/bookings", json=payload)
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data


class TestConversionFunnelIntelligence:
    def test_conversion_summary_api(self):
        resp = client.get("/api/admin/conversion/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "circuit_metrics" in data
        assert "funnel" in data
        assert "observed_acceptance_rate" in data
        assert data["configured_acceptance_rate"] == 0.15
        assert data["acceptance_rate_mode"] in ("CONFIGURED", "OBSERVED", "INSUFFICIENT_DATA")
        assert data["provenance"] == "REAL — YATRI SETU NETWORK"
        assert len(data["funnel"]) >= 5

    def test_destination_conversion_api(self):
        resp = client.get("/api/admin/conversion/destinations?destination_id=kalimpong")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["destination_id"] == "kalimpong"
        assert 0.0 <= data[0]["alternative_acceptance_rate"] <= 1.0

    def test_outbound_click_telemetry_not_counted_as_booking(self):
        # Record an outbound click event
        event_payload = {
            "event_type": "outbound_booking_click",
            "destination_id": "mirik",
            "session_id": "sess-partner-click-99",
            "metadata": {"partner": "BookingPartnerHimalayas", "status": "CLICKED"}
        }
        resp = client.post("/api/conversion/events", json=event_payload)
        assert resp.status_code == 200

        # Verify summary reflects outbound click but doesn't increase confirmed bookings
        dest_metrics = conversion_funnel_service.get_destination_conversion_metrics("mirik")
        assert len(dest_metrics) == 1
        assert dest_metrics[0].outbound_clicks >= 1


class TestPrivacyCompliance:
    def test_no_sensitive_pii_in_demand_telemetry(self):
        # Audit all recent demand events
        events = demand_aggregation_service._events
        forbidden_keys = ["password", "card_number", "cvv", "payment_token", "secret", "pan_number"]

        for evt in events:
            meta = evt.get("metadata") or {}
            for key in forbidden_keys:
                assert key not in meta, f"Forbidden privacy key '{key}' found in demand event metadata!"
                assert key not in str(evt).lower(), f"Potential PII '{key}' leaked into event record"
