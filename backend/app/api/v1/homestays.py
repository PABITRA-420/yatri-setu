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

@router.post("/bookings", response_model=HomestayBookingResponse)
def create_booking(req: HomestayBookingRequest):
    """Simulates a confirmed rural homestay booking with verified travel pass QR payload."""
    matched_homestay = homestay_repository.resolve_for_booking(req.homestay_id)
    if not matched_homestay:
        raise HTTPException(status_code=404, detail=f"Homestay '{req.homestay_id}' not found")

    nights = 3
    subtotal = matched_homestay.price_per_night_inr * nights
    community_fund = int(round(subtotal * 0.05)) # 5% to Village Gram Panchayat
    platform_fee = int(round(subtotal * 0.05)) # 5% platform maintenance fee
    host_earning = subtotal - platform_fee # 95% of stay or 90% direct
    total = subtotal + community_fund

    booking_id = f"YS-BK-{uuid.uuid4().hex[:6].upper()}"
    qr_payload = f"YATRI-SETU-VERIFIED:{booking_id}:{matched_homestay.id}:{req.traveler_name}:STAMP_OK"

    booking_response = HomestayBookingResponse(
        booking_id=booking_id,
        homestay=matched_homestay,
        traveler_name=req.traveler_name,
        traveler_phone=req.traveler_phone,
        check_in_date=req.check_in_date,
        check_out_date=req.check_out_date,
        number_of_guests=req.number_of_guests,
        total_nights=nights,
        subtotal_inr=subtotal,
        community_fund_contribution_inr=community_fund,
        platform_fee_inr=platform_fee,
        host_earning_inr=host_earning,
        total_amount_inr=total,
        payment_status="PROTOTYPE_ESCROW_CONFIRMED",
        status="CONFIRMED",
        digital_pass_qr_payload=qr_payload,
        host_contact=f"+91 98320 {uuid.uuid4().int % 90000 + 10000}",
        homestay_gps="27.0667° N, 88.4667° E",
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    BOOKINGS_DB[booking_id] = booking_response
    # Record booking event
    demand_aggregation_service.record_event(
        event_type=DemandEventType.BOOKING.value,
        destination_id=matched_homestay.destination_id,
        session_id=booking_id,
        metadata={
            "rooms": 1,
            "guests": req.number_of_guests,
            "total_amount": total,
        },
    )
    return booking_response

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
