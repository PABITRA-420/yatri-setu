import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.data.seed_data import HOMESTAYS_DATA
from app.models.homestay import (
    Homestay, HomestayBookingRequest, HomestayBookingResponse, TripDetailsResponse
)
from app.services.homestay_repository import homestay_repository
from app.services.demand_aggregation_service import demand_aggregation_service
from app.models.demand import DemandEventType

router = APIRouter(tags=["Homestays & Bookings"])

# Simple in-memory booking store for demo session
BOOKINGS_DB = {}

# In‑memory store for trip start timestamps (idempotent trip start)
STARTED_TRIPS: dict[str, datetime] = {}

@router.get("/homestays", response_model=List[Homestay])
def list_homestays(
    destination_id: Optional[str] = Query(None, description="Filter by destination id, e.g., 'kalimpong'"),
    max_price: Optional[int] = Query(None, description="Filter by maximum price per night")
):
    """Lists verified rural homestays.
    Returns only homestays where verification_status is VERIFIED or PUBLISHED.
    Supports optional filtering by destination_id and max_price.
    """
    return homestay_repository.list_homestays(
        destination_id=destination_id,
        max_price=max_price,
        visible_only=True
    )

@router.get("/homestays/{homestay_id}", response_model=Homestay)
def get_homestay_details(homestay_id: str):
    """Get single homestay profile from authoritative repository."""
    hs = homestay_repository.get_homestay(homestay_id, visible_only=True)
    if not hs:
        raise HTTPException(status_code=404, detail=f"Homestay '{homestay_id}' not found")
    return hs

from app.services.booking.service import booking_lifecycle_service
from app.services.booking.schemas import BookingState, BookingFailureReason, BookingRecord
from app.services.availability.service import availability_service
from app.services.availability.schemas import HomestayAvailabilitySnapshot

@router.post("/bookings", response_model=HomestayBookingResponse)
def create_booking(
    req: HomestayBookingRequest,
    idempotency_key: Optional[str] = Query(None, description="Optional client idempotency key")
):
    """
    Creates and processes a verified homestay booking through the deterministic state machine.
    Enforces atomic room reservation, double-booking prevention, and first-party event emission.
    """
    record, legacy_resp = booking_lifecycle_service.create_booking(
        req=req,
        idempotency_key=idempotency_key,
        auto_confirm=True
    )

    if record.state == BookingState.FAILED:
        status_code = 404 if record.failure_reason == BookingFailureReason.INVALID_HOMESTAY else 409
        detail_msg = (
            f"Homestay '{req.homestay_id}' not found"
            if record.failure_reason == BookingFailureReason.INVALID_HOMESTAY
            else (record.failure_detail or "Unable to confirm booking: room sold out or unavailable")
        )
        raise HTTPException(status_code=status_code, detail=detail_msg)

    if legacy_resp:
        BOOKINGS_DB[record.booking_id] = legacy_resp
        return legacy_resp

    raise HTTPException(status_code=500, detail="Internal booking processing error")


@router.get("/bookings/{booking_id}", response_model=BookingRecord)
def get_booking_details(booking_id: str):
    """Returns lifecycle state and audit trail for a booking."""
    record = booking_lifecycle_service.get_booking(booking_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")
    return record


@router.post("/bookings/{booking_id}/confirm", response_model=BookingRecord)
def confirm_booking(booking_id: str):
    """Confirms a booking currently in PENDING_CONFIRMATION."""
    try:
        return booking_lifecycle_service.confirm_booking(booking_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/bookings/{booking_id}/cancel", response_model=BookingRecord)
def cancel_booking(
    booking_id: str,
    reason: Optional[str] = Query(None, description="Optional cancellation reason")
):
    """Cancels a confirmed booking and atomically releases reserved room units back to ledger."""
    try:
        return booking_lifecycle_service.cancel_booking(booking_id, reason=reason)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/homestays/{homestay_id}/availability", response_model=HomestayAvailabilitySnapshot)
def get_homestay_availability(
    homestay_id: str,
    date: Optional[str] = Query(None, description="Target date in YYYY-MM-DD format (defaults to today)")
):
    """Returns date-aware accommodation availability snapshot for a specific homestay."""
    rec = homestay_repository.get_raw_record(homestay_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Homestay '{homestay_id}' not found")
    return availability_service.get_homestay_availability(homestay_id, target_date=date)


@router.get("/trips/{trip_id}", response_model=TripDetailsResponse)
def get_trip_details(trip_id: str):
    """Returns active trip companion data, travel pass, emergency contact, and packing guidelines."""
    # If booking exists in DB, use it, else return representative trip demo
    b = BOOKINGS_DB.get(trip_id)
    homestay_name = b.homestay.title if b else "Pineview Orchid Retreat & Homestay"
    dest_name = b.homestay.destination_name if b else "Kalimpong"
    dest_id = b.homestay.destination_id if b else "kalimpong"
    traveler_count = b.number_of_guests if b else 2
    dates = f"{b.check_in_date} to {b.check_out_date}" if b else "Oct 12 - Oct 15, 2026"

    return TripDetailsResponse(
        trip_id=trip_id,
        destination_name=dest_name,
        destination_id=dest_id,
        homestay_name=homestay_name,
        dates=dates,
        status="Active Upcoming Journey",
        travelers_count=traveler_count,
        digital_pass_code=f"YS-PASS-{trip_id.replace('YS-BK-', '')}",
        emergency_pin_active=True,
        weather_alert="Pleasant Mountain Sun: 14°C - 21°C. Light showers possible in late evening.",
        host_support_number="+91 98320 87123 (Pemba Sherpa)",
        local_panchayat_contact="+91 3552 255401 (Kalimpong Block II Nodal Desk)",
        check_in_location="Atisha Road, Upper Cart Road, Kalimpong",
        packing_checklist=[
            "Light breathable fleece jacket for chilly ridge winds",
            "Sturdy trekking sneakers for pine trails & orchid gardens",
            "Refillable water canteen (100% single-use plastic free village)",
            "Government Photo ID (Physical or DigiLocker) for Forest Checkpost",
            "Offline digital Yatri Setu Travel Pass QR saved on device"
        ]
    )
