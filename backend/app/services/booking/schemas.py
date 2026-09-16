"""
Booking Lifecycle Schemas for Yatri Setu (Milestone 7E).
Defines deterministic booking state machine, failure classifications, and transition records.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BookingState(str, Enum):
    INITIATED = "INITIATED"
    AVAILABILITY_CHECKED = "AVAILABILITY_CHECKED"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class BookingFailureReason(str, Enum):
    SOLD_OUT = "SOLD_OUT"
    INVALID_DATE = "INVALID_DATE"
    INVALID_HOMESTAY = "INVALID_HOMESTAY"
    CONFLICT = "CONFLICT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN = "UNKNOWN"


class BookingTransition(BaseModel):
    from_state: BookingState
    to_state: BookingState
    timestamp: str
    reason: Optional[str] = None


class BookingRecord(BaseModel):
    booking_id: str
    homestay_id: str
    destination_id: str
    traveler_name: str
    traveler_phone: str
    traveler_email: str
    emergency_contact: str
    check_in_date: str
    check_out_date: str
    number_of_guests: int
    rooms_booked: int = 1
    total_amount_inr: int
    subtotal_inr: int
    community_fund_contribution_inr: int
    platform_fee_inr: int
    host_earning_inr: int
    state: BookingState = BookingState.INITIATED
    failure_reason: Optional[BookingFailureReason] = None
    failure_detail: Optional[str] = None
    transitions: List[BookingTransition] = Field(default_factory=list)
    idempotency_key: Optional[str] = None
    digital_pass_qr_payload: Optional[str] = None
    host_contact: Optional[str] = None
    created_at: str
    updated_at: str
