from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from app.models.host import (
    Host, HomestayListing, AvailabilityRecord, HostOnboardingRequest,
    VoiceDraftRequest, VoiceDraftResponse
)
from app.services.host_service import host_service
from app.services.rural.service import rural_operations_service
from app.services.rural.schemas import (
    HostProfile, HostDashboardData, HostNotification, HostActiveStatus
)

router = APIRouter(prefix="/hosts", tags=["Host Ecosystem"])

# Also provide /host alias router for direct specification compliance
alias_router = APIRouter(prefix="/host", tags=["Host Ecosystem"])


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


@router.get("/profile", response_model=HostProfile)
def get_current_host_profile():
    """
    Returns normalized M7G host profile for default host.
    """
    return rural_operations_service.get_default_host()


@router.get("/{host_id}/profile", response_model=HostProfile)
def get_host_normalized_profile(host_id: str):
    profile = rural_operations_service.get_host_profile(host_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Host profile '{host_id}' not found")
    return profile


@router.get("/dashboard")
def get_default_host_dashboard():
    """
    Default host dashboard for the current active prototype host.
    """
    return get_host_dashboard("host-kalim-01")


@router.get("/{host_id}/dashboard")
def get_host_dashboard(host_id: str):
    """
    Returns both backward-compatible fields and normalized M7G dashboard metrics.
    Connects first-party confirmed bookings to host earnings.
    """
    legacy_host = host_service.get_host_by_id(host_id)
    if not legacy_host:
        legacy_host = host_service.get_default_host()

    listings = host_service.list_listings_by_host(legacy_host.id)
    earnings_summary = host_service.get_host_earnings_summary(legacy_host.id)

    # Normalized M7G Data
    m7g_data = rural_operations_service.get_host_dashboard_data(legacy_host.id)

    return {
        # Legacy compatibility keys
        "host": legacy_host,
        "listings_count": len(listings),
        "listings": listings,
        "earnings_summary": earnings_summary,
        "verification_status": legacy_host.verification.status,
        # Normalized M7G keys
        "profile": m7g_data.profile,
        "active_homestays": m7g_data.active_homestays,
        "booking_snapshot": m7g_data.booking_snapshot,
        "demand_snapshot": m7g_data.demand_snapshot,
        "economic_summary": m7g_data.economic_summary,
        "recent_notifications": m7g_data.recent_notifications,
        "provenance": m7g_data.provenance
    }


@router.get("/notifications", response_model=List[HostNotification])
def get_default_host_notifications():
    return rural_operations_service.get_host_notifications("host-kalim-01")


@router.get("/{host_id}/notifications", response_model=List[HostNotification])
def get_host_notifications(host_id: str):
    return rural_operations_service.get_host_notifications(host_id)


@router.post("/{host_id}/suspend", response_model=HostProfile)
def suspend_host(host_id: str, reason: str = Body("Administrative policy suspension", embed=True)):
    host = rural_operations_service.suspend_host(host_id, reason=reason)
    if not host:
        raise HTTPException(status_code=404, detail=f"Host '{host_id}' not found")
    return host


@router.get("/{host_id}", response_model=Host)
def get_host_profile_by_id(host_id: str):
    host = host_service.get_host_by_id(host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host


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
    return host_service.parse_voice_listing(req)


# Mount matching handlers onto alias_router for /host/* URLs
@alias_router.get("/profile", response_model=HostProfile)
def alias_get_current_host_profile():
    return get_current_host_profile()

@alias_router.get("/dashboard")
def alias_get_default_host_dashboard():
    return get_default_host_dashboard()

@alias_router.get("/notifications", response_model=List[HostNotification])
def alias_get_default_host_notifications():
    return get_default_host_notifications()
