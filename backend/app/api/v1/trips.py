import datetime
from fastapi import APIRouter, HTTPException
from app.models.homestay import TripDetailsResponse
from app.models.demand import DemandEventType
from app.services.demand_aggregation_service import demand_aggregation_service
from app.api.v1.homestays import BOOKINGS_DB, STARTED_TRIPS, get_trip_details

router = APIRouter(tags=["Trips"])

@router.post("/trips/{trip_id}/start", response_model=TripDetailsResponse)
def start_trip(trip_id: str):
    """Mark a trip as started, record a TripStartEvent, and return trip details.
    Idempotent – if already started, no new event is recorded.
    """
    booking = BOOKINGS_DB.get(trip_id)
    destination_id = booking.homestay.destination_id if booking and hasattr(booking, "homestay") else "kalimpong"

    # Idempotent start handling
    if trip_id not in STARTED_TRIPS:
        # Record start timestamp
        STARTED_TRIPS[trip_id] = datetime.datetime.utcnow()
        # Record TripStartEvent
        demand_aggregation_service.record_event(
            event_type=DemandEventType.TRIP_START.value,
            destination_id=destination_id,
            session_id=trip_id,
            metadata={"trip_id": trip_id},
        )
    # Return trip details
    trip = get_trip_details(trip_id)
    trip.status = "Journey In Progress"
    return trip
