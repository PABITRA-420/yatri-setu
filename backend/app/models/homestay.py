from typing import List, Optional
from pydantic import BaseModel, Field

class HostInfo(BaseModel):
    name: str
    avatar_url: str
    experience_years: int
    languages: List[str]
    about: str
    verified_panchayat: bool
    response_rate: str

class Homestay(BaseModel):
    id: str
    destination_id: str
    destination_name: str
    title: str
    tagline: str
    address: str
    price_per_night_inr: int
    rating: float
    reviews_count: int
    room_type: str
    max_guests: int
    amenities: List[str]
    images: List[str]
    host: HostInfo
    community_fund_contribution_percent: int
    special_activity: str # e.g. "Orchid cultivation workshop & Nepali organic cooking"
    verified: bool = True
    panchayat_verified: bool = True
    sustainable_stay_badge: bool = True
    host_id: Optional[str] = None
    verification_status: str = "VERIFIED"

class HomestayBookingRequest(BaseModel):
    homestay_id: str
    traveler_name: str
    traveler_phone: str
    traveler_email: str
    emergency_contact: str
    check_in_date: str
    check_out_date: str
    number_of_guests: int
    special_requests: Optional[str] = None

class HomestayBookingResponse(BaseModel):
    booking_id: str
    homestay: Homestay
    traveler_name: str
    traveler_phone: str
    check_in_date: str
    check_out_date: str
    number_of_guests: int
    total_nights: int
    subtotal_inr: int
    community_fund_contribution_inr: int
    total_amount_inr: int
    platform_fee_inr: int = 0
    host_earning_inr: int = 0
    payment_status: str = "PROTOTYPE_ESCROW_CONFIRMED"
    status: str # "CONFIRMED", "PENDING"
    digital_pass_qr_payload: str
    host_contact: str
    homestay_gps: str
    created_at: str

class TripDetailsResponse(BaseModel):
    trip_id: str
    destination_name: str
    destination_id: str
    homestay_name: str
    dates: str
    status: str
    travelers_count: int
    digital_pass_code: str
    emergency_pin_active: bool
    weather_alert: str
    host_support_number: str
    local_panchayat_contact: str
    check_in_location: str
    packing_checklist: List[str]
