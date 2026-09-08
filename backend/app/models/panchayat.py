from typing import List, Optional
from pydantic import BaseModel
from app.models.host import VerificationEvent

class CommunityFundProject(BaseModel):
    id: str
    title: str
    category: str # "Trail Restoration", "Solar Lighting", "Plastic Waste Management", "Spring Water Rejuvenation"
    budget_inr: int
    status: str # "COMPLETED", "IN_PROGRESS", "PROPOSED"
    completion_date: str
    impact_description: str

class PanchayatVerificationItem(BaseModel):
    listing_id: str
    host_id: str
    host_name: str
    host_phone: str
    homestay_title: str
    destination_id: str
    destination_name: str
    village: str
    panchayat_name: str
    submitted_at: str
    verification_status: str # "SUBMITTED", "UNDER_REVIEW", "VERIFIED", "REJECTED", "PUBLISHED"
    id_proof_type: str
    id_proof_masked: str
    rooms_count: int
    price_per_night_inr: int
    amenities: List[str]
    sustainability_attributes: List[str]
    history: List[VerificationEvent] = []

class PanchayatDecisionRequest(BaseModel):
    action: str # "APPROVE" or "REJECT"
    reason: str
    reviewer_name: str = "Panchayat Officer Pemba Norbu"

class PanchayatDecisionResponse(BaseModel):
    listing_id: str
    previous_status: str
    new_status: str
    updated_at: str
    reviewer_name: str
    decision_notes: str

class PanchayatDashboard(BaseModel):
    panchayat_name: str
    block: str
    district: str
    state: str
    verified_homestays_count: int
    pending_verifications_count: int
    local_guides_count: int
    total_experiences_count: int
    tourist_arrivals_this_month: int
    local_booking_revenue_inr: int
    community_fund_balance_inr: int
    tourism_pressure_relief_index: float # 0.0 to 1.0 (e.g. 0.38 = 38% pressure reduction)
    community_projects: List[CommunityFundProject]
    recent_verifications: List[PanchayatVerificationItem]
