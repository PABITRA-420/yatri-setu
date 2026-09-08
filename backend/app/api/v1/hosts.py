from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from app.models.host import (
    Host, HomestayListing, AvailabilityRecord, HostOnboardingRequest,
    VoiceDraftRequest, VoiceDraftResponse
)
from app.services.host_service import host_service

router = APIRouter(prefix="/hosts", tags=["Host Ecosystem"])

@router.post("/onboard")
def onboard_host(req: HostOnboardingRequest):
    """
    Onboards a rural homestay host and creates their listing in SUBMITTED state.
    """
    return host_service.register_host_and_listing(req)

@router.get("/me", response_model=Host)
def get_current_host():
    """
    Returns default active host profile (Pemba Sherpa) for prototype demonstration.
    """
    return host_service.get_default_host()

@router.get("/{host_id}", response_model=Host)
def get_host_profile(host_id: str):
    host = host_service.get_host_by_id(host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host

@router.get("/{host_id}/dashboard")
def get_host_dashboard(host_id: str):
    host = host_service.get_host_by_id(host_id)
    if not host:
        host = host_service.get_default_host()
    
    listings = host_service.list_listings_by_host(host.id)
    earnings_summary = host_service.get_host_earnings_summary(host.id)
    
    return {
        "host": host,
        "listings_count": len(listings),
        "listings": listings,
        "earnings_summary": earnings_summary,
        "verification_status": host.verification.status
    }

@router.get("/{host_id}/listings", response_model=List[HomestayListing])
def get_host_listings(host_id: str):
    return host_service.list_listings_by_host(host_id)

@router.get("/{host_id}/earnings")
def get_host_earnings(host_id: str):
    return host_service.get_host_earnings_summary(host_id)

@router.get("/{host_id}/availability", response_model=List[AvailabilityRecord])
def get_host_availability(
    host_id: str,
    homestay_id: Optional[str] = Query(None)
):
    h_id = homestay_id or "hs-kalim-01"
    return host_service.get_availability(h_id)

@router.post("/{host_id}/availability", response_model=AvailabilityRecord)
def update_host_availability(
    host_id: str,
    homestay_id: str = Body(..., embed=True),
    date_str: str = Body(..., embed=True),
    is_available: bool = Body(..., embed=True),
    price_override_inr: Optional[int] = Body(None, embed=True)
):
    return host_service.toggle_availability(homestay_id, date_str, is_available, price_override_inr)

@router.post("/voice-draft", response_model=VoiceDraftResponse)
def parse_voice_draft(req: VoiceDraftRequest):
    """
    AI Voice Listing Assistant:
    Parses spoken description of rural homestay into structured listing draft.
    Strictly safeguards pricing, verification status, identity, and availability.
    """
    return host_service.parse_voice_listing(req)
