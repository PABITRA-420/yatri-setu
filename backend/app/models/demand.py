"""
Demand Events and Intelligence Models (Milestone 7A)
Defines first-party demand event schemas, demand aggregation metrics,
provenance indicators, capacity check attributes, and live pressure responses.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.models.observation import ProviderMode, DataQuality


class DemandEventType(str, Enum):
    SEARCH = "search"
    BOOKING = "booking"
    AVAILABILITY = "availability"
    TRIP_START = "trip_start"
    DESTINATION_SELECTION = "destination_selection"
    ALTERNATIVE_ACCEPTANCE = "alternative_acceptance"
    # Milestone 7E First-Party Conversion & Lifecycle Events
    BOOKING_INITIATED = "booking_initiated"
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_FAILED = "booking_failed"
    BOOKING_CANCELLED = "booking_cancelled"
    AVAILABILITY_CHECKED = "availability_checked"
    OUTBOUND_BOOKING_CLICK = "outbound_booking_click"
    ALTERNATIVE_VIEWED = "alternative_viewed"
    DATE_SELECTED = "date_selected"
    DESTINATION_VIEW = "destination_view"


# ─── Demand Event Schemas ───────────────────────────────────────────────────

class BaseDemandEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    destination_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "YATRI_SETU_NETWORK"


class SearchEvent(BaseDemandEvent):
    event_type: str = DemandEventType.SEARCH.value
    query: Optional[str] = None
    matched_destinations: List[str] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)


class BookingEvent(BaseDemandEvent):
    event_type: str = DemandEventType.BOOKING.value
    homestay_id: Optional[str] = None
    total_amount_inr: Optional[float] = None
    guests_count: Optional[int] = 2
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None


class AvailabilityEvent(BaseDemandEvent):
    event_type: str = DemandEventType.AVAILABILITY.value
    homestay_id: Optional[str] = None
    date: Optional[str] = None
    is_available: bool = True
    rooms_available: int = 1
    price_override_inr: Optional[int] = None


class TripStartEvent(BaseDemandEvent):
    event_type: str = DemandEventType.TRIP_START.value
    trip_id: Optional[str] = None
    party_size: int = 2
    check_in_location: Optional[str] = None


class DestinationSelectionEvent(BaseDemandEvent):
    event_type: str = DemandEventType.DESTINATION_SELECTION.value
    referrer_view: Optional[str] = "explore"
    search_query: Optional[str] = None


class AlternativeAcceptanceEvent(BaseDemandEvent):
    event_type: str = DemandEventType.ALTERNATIVE_ACCEPTANCE.value
    origin_destination_id: Optional[str] = None
    original_destination_id: Optional[str] = None
    accepted_alternative_id: Optional[str] = None
    alternative_destination_id: Optional[str] = None
    similarity_score: Optional[int] = None
    estimated_cost_diff_percent: Optional[int] = None
    crowd_reduction_percent: Optional[int] = None

    def __init__(self, **data: Any):
        if "original_destination_id" in data and not data.get("origin_destination_id"):
            data["origin_destination_id"] = data["original_destination_id"]
        elif "origin_destination_id" in data and not data.get("original_destination_id"):
            data["original_destination_id"] = data["origin_destination_id"]
        if "alternative_destination_id" in data and not data.get("accepted_alternative_id"):
            data["accepted_alternative_id"] = data["alternative_destination_id"]
        elif "accepted_alternative_id" in data and not data.get("alternative_destination_id"):
            data["alternative_destination_id"] = data["accepted_alternative_id"]
        super().__init__(**data)


# ─── Derived Safe Tourist Signals ──────────────────────────────────────────

class TouristSignals(BaseModel):
    demand_trend_label: str = Field("Demand is steady", description="Safe descriptive trend label (e.g. 'Demand is rising')")
    booking_pressure_label: str = Field("Normal booking pace", description="Safe booking pressure indicator (e.g. 'High booking pressure')")
    recommendation_label: Optional[str] = Field(None, description="Safe alternative recommendation notice (e.g. 'Alternative destination recommended')")
    is_alternative_advised: bool = False


# ─── Capacity Metrics ──────────────────────────────────────────────────────

class DestinationCapacityStatus(BaseModel):
    destination_id: str
    total_homestay_rooms: int
    rooms_available: int
    rooms_booked: int
    capacity_available: int
    capacity_pressure: float = Field(..., ge=0.0, le=100.0, description="Percentage of Yatri Setu capacity occupied (0-100%)")
    capacity_threshold: float = 85.0
    absorber_status: str = Field("OPTIMAL_ABSORBER", description="OPTIMAL_ABSORBER, VIABLE_ABSORBER, or CAPACITY_CONSTRAINED")
    is_constrained: bool = False


# ─── Demand Aggregation Metrics ───────────────────────────────────────────

class DemandMetrics(BaseModel):
    destination_id: str
    destination_name: str
    search_count_24h: int = 0
    search_count_7d: int = 0
    booking_count_24h: int = 0
    booking_count_7d: int = 0
    booking_conversion: float = Field(0.0, ge=0.0, le=1.0, description="Booking conversion ratio")
    availability_pressure: float = Field(0.0, ge=0.0, le=100.0, description="Capacity pressure percentage (0-100)")
    alternative_acceptance_rate: float = Field(0.0, ge=0.0, le=1.0, description="Rate of accepted alternative suggestions")
    trend_percent: float = Field(0.0, description="24h demand velocity change vs 7d average (%)")
    trend_direction: str = "STABLE" # RISING, STABLE, DECLINING
    normalized_search_demand: float = Field(..., ge=0.0, le=100.0, description="0-100 normalized search demand index (LEADING INDICATOR)")
    normalized_booking_demand: float = Field(..., ge=0.0, le=100.0, description="0-100 normalized booking demand index (Yatri Setu Network)")
    source: str = "YATRI_SETU_NETWORK"
    provider_mode: ProviderMode = ProviderMode.REAL
    confidence: float = Field(0.94, ge=0.0, le=1.0)
    data_quality: DataQuality = DataQuality.HIGH
    provenance_label: str = "REAL — YATRI SETU NETWORK"
    is_leading_indicator: bool = True
    tourist_signals: TouristSignals
    capacity: DestinationCapacityStatus
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    notes: str = "First-party demand signal observed across Yatri Setu Network. Search demand is a leading indicator, not direct physical presence."


# ─── Circuit & Admin Telemetry Schemas ─────────────────────────────────────

class CircuitDemandSummary(BaseModel):
    total_searches_24h: int
    total_searches_7d: int
    total_bookings_24h: int
    total_bookings_7d: int
    overall_booking_conversion: float
    highest_demand_hub: str
    primary_rural_absorber: str
    source: str = "YATRI_SETU_NETWORK"
    provider_mode: str = "REAL"
    provenance_label: str = "REAL — YATRI SETU NETWORK"


class CircuitDemandResponse(BaseModel):
    circuit_id: str = "darjeeling_kalimpong_circuit"
    circuit_name: str = "Eastern Himalayan Tourism Circuit"
    summary: CircuitDemandSummary
    destinations: Dict[str, DemandMetrics]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class EventIngestRequest(BaseModel):
    event_type: DemandEventType
    destination_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventIngestResponse(BaseModel):
    status: str = "RECORDED"
    event_id: str
    destination_id: str
    event_type: str
    timestamp: datetime
    source: str = "YATRI_SETU_NETWORK"
    provenance_label: str = "REAL — FIRST-PARTY"


class AdminDemandOverview(BaseModel):
    total_events_recorded: int
    events_24h_count: int
    events_7d_count: int
    event_breakdown: Dict[str, int]
    conversion_funnel: Dict[str, int]
    circuit_summary: CircuitDemandSummary
    provenance_audit: Dict[str, Any]
    recent_events_preview: List[Dict[str, Any]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
