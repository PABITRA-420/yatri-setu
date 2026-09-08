from typing import List, Optional
from pydantic import BaseModel, Field

class VerificationEvent(BaseModel):
    status: str # "SUBMITTED", "UNDER_REVIEW", "VERIFIED", "REJECTED", "PUBLISHED"
    timestamp: str
    actor: str # e.g. "Host (Initial Registration)", "Panchayat Officer Pemba Norbu"
    notes: str

class HostVerification(BaseModel):
    status: str = "SUBMITTED" # "SUBMITTED", "UNDER_REVIEW", "VERIFIED", "REJECTED", "PUBLISHED"
    id_proof_type: str = "AADHAAR_PROTOTYPE"
    id_proof_number_masked: str = "XXXX-XXXX-8921"
    panchayat_name: str
    block: str
    district: str = "Kalimpong"
    submitted_at: str
    verified_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    history: List[VerificationEvent] = []

class Host(BaseModel):
    id: str
    name: str
    phone: str
    email: str
    village: str
    panchayat_name: str
    languages: List[str]
    bio: str
    avatar_url: str
    experience_years: int = 4
    verification: HostVerification
    created_at: str

class HomestayListing(BaseModel):
    id: str
    host_id: str
    destination_id: str
    destination_name: str
    title: str
    tagline: str
    address: str
    village: str
    panchayat_name: str
    price_per_night_inr: int
    room_type: str
    max_guests: int
    rooms_count: int
    amenities: List[str]
    sustainability_attributes: List[str]
    images: List[str]
    special_activity: str
    rating: float = 4.9
    reviews_count: int = 12
    verification_status: str = "SUBMITTED" # SUBMITTED, UNDER_REVIEW, VERIFIED, REJECTED, PUBLISHED
    is_published: bool = True
    community_fund_contribution_percent: int = 5

class AvailabilityRecord(BaseModel):
    homestay_id: str
    date: str # YYYY-MM-DD
    is_available: bool = True
    price_override_inr: Optional[int] = None
    blocked_reason: Optional[str] = None

class HostEarningBreakdown(BaseModel):
    booking_id: str
    homestay_id: str
    homestay_name: str
    guest_name: str
    check_in_date: str
    check_out_date: str
    nights: int
    gross_booking_value: int
    platform_fee: int # 5%
    community_fund_contribution: int # 5%
    net_host_earning: int # 90%
    payout_status: str # "IN_ESCROW_CONFIRMED", "DISBURSED"
    created_at: str

class HostOnboardingRequest(BaseModel):
    name: str
    phone: str
    email: str
    village: str
    panchayat_name: str
    destination_id: str
    languages: List[str]
    bio: str
    homestay_title: str
    tagline: str
    address: str
    room_type: str
    rooms_count: int = 2
    max_guests: int = 4
    price_per_night_inr: int
    amenities: List[str]
    sustainability_attributes: List[str]
    special_activity: str
    local_experience_title: Optional[str] = None
    local_experience_desc: Optional[str] = None
    local_experience_price: Optional[int] = None

class VoiceDraftRequest(BaseModel):
    spoken_text: str

class VoiceDraftResponse(BaseModel):
    original_transcript: str
    suggested_title: str
    suggested_tagline: str
    detected_destination_id: str
    detected_village: str
    detected_room_type: str
    suggested_rooms_count: int
    detected_amenities: List[str]
    detected_sustainability_attributes: List[str]
    suggested_experiences: List[str]
    # Safety guardrails
    price_requires_host_input: bool = True
    verification_status: str = "SUBMITTED"
    warning_guardrail: str = "AI has not set price, identity, or verification status. Please review and specify your pricing and identity documents manually."
