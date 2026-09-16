from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from app.models.panchayat import (
    PanchayatDashboard, PanchayatVerificationItem, PanchayatDecisionRequest,
    PanchayatDecisionResponse
)
from app.services.panchayat_service import panchayat_service
from app.services.rural.service import rural_operations_service
from app.services.rural.schemas import (
    LocalAuthorityProfile, PanchayatNotification, DestinationLocalEconomy
)

router = APIRouter(prefix="/panchayat", tags=["Gram Panchayat Administration"])


@router.get("/profile", response_model=LocalAuthorityProfile)
def get_panchayat_profile(
    destination_id: Optional[str] = Query("kalimpong", description="Destination identifier")
):
    """
    Returns normalized local authority profile for Panchayat desk.
    """
    dest = (destination_id or "kalimpong").lower().strip()
    auth = rural_operations_service._authorities.get(dest)
    if not auth:
        auth = rural_operations_service._authorities.get("kalimpong")
    return auth


@router.get("/dashboard", response_model=PanchayatDashboard)
def get_panchayat_dashboard(
    destination_id: Optional[str] = Query(None, description="Optional destination filter")
):
    """
    Returns administrative overview for Gram Panchayat Nodal Desk.
    Includes legacy verified homestay metrics, community fund reserves,
    and normalized M7G capacity advisories, local economy breakdown, and safety summary.
    """
    dest = (destination_id or "kalimpong").lower().strip()
    legacy_dash = panchayat_service.get_dashboard()
    m7g_data = rural_operations_service.get_panchayat_dashboard_data(dest)

    # Blend legacy dashboard with M7G real-time operational metrics
    return PanchayatDashboard(
        panchayat_name=m7g_data.authority.name,
        block=m7g_data.authority.jurisdiction,
        district=m7g_data.authority.destination_name,
        state="West Bengal",
        verified_homestays_count=m7g_data.local_economy.verified_hosts_count + 14,
        pending_verifications_count=legacy_dash.pending_verifications_count,
        local_guides_count=26,
        total_experiences_count=18,
        tourist_arrivals_this_month=legacy_dash.tourist_arrivals_this_month,
        local_booking_revenue_inr=m7g_data.local_economy.gross_booking_value_inr,
        community_fund_balance_inr=legacy_dash.community_fund_balance_inr + m7g_data.local_economy.community_fund_accrued_inr,
        tourism_pressure_relief_index=legacy_dash.tourism_pressure_relief_index,
        community_projects=legacy_dash.community_projects,
        recent_verifications=legacy_dash.recent_verifications,
        # M7G Operational Fields
        authority=m7g_data.authority.model_dump() if hasattr(m7g_data.authority, "model_dump") else m7g_data.authority.dict(),
        tourism_flow=m7g_data.tourism_flow,
        rural_ecosystem=m7g_data.rural_ecosystem,
        local_economy=m7g_data.local_economy.model_dump() if hasattr(m7g_data.local_economy, "model_dump") else m7g_data.local_economy.dict(),
        safety_summary=m7g_data.safety_summary,
        notifications=[(n.model_dump() if hasattr(n, "model_dump") else n.dict()) for n in m7g_data.notifications],
        capacity_warning=m7g_data.capacity_warning,
        provenance=m7g_data.provenance
    )


@router.get("/notifications", response_model=List[PanchayatNotification])
def list_panchayat_notifications(
    destination_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """
    Returns active and past capacity, flow, weather, and safety advisory notifications for Panchayat desks.
    """
    return rural_operations_service.list_panchayat_notifications(destination_id=destination_id, status=status)


@router.post("/notifications/{notification_id}/acknowledge", response_model=PanchayatNotification)
def acknowledge_panchayat_notification(
    notification_id: str,
    operator_name: str = Body("Panchayat Desk Operator", embed=True)
):
    """
    Operator acknowledges an advisory notification.
    """
    notif = rural_operations_service.acknowledge_panchayat_notification(notification_id, operator_name=operator_name)
    if not notif:
        raise HTTPException(status_code=404, detail=f"Notification '{notification_id}' not found")
    return notif


@router.post("/notifications/{notification_id}/resolve", response_model=PanchayatNotification)
def resolve_panchayat_notification(
    notification_id: str,
    operator_name: str = Body("Panchayat Desk Operator", embed=True),
    resolution_notes: Optional[str] = Body(None, embed=True)
):
    """
    Operator resolves an advisory notification with operational remarks.
    """
    notif = rural_operations_service.resolve_panchayat_notification(
        notification_id,
        operator_name=operator_name,
        resolution_notes=resolution_notes
    )
    if not notif:
        raise HTTPException(status_code=404, detail=f"Notification '{notification_id}' not found")
    return notif


@router.get("/economy", response_model=DestinationLocalEconomy)
def get_destination_economy(
    destination_id: Optional[str] = Query("kalimpong")
):
    """
    Returns destination-level local economic impact and host participation metrics.
    """
    dest = (destination_id or "kalimpong").lower().strip()
    return rural_operations_service.get_destination_local_economy(dest)


@router.get("/verifications", response_model=List[PanchayatVerificationItem])
def list_verification_queue(
    status: Optional[str] = Query(None, description="Filter by status: SUBMITTED, UNDER_REVIEW, VERIFIED, REJECTED")
):
    """
    Returns listings pending physical or documentary certification.
    """
    return panchayat_service.list_verifications(status=status)


@router.post("/verifications/{listing_id}/decision", response_model=PanchayatDecisionResponse)
def make_verification_decision(
    listing_id: str,
    req: PanchayatDecisionRequest
):
    """
    Approves or rejects a homestay listing with official audit notes.
    """
    try:
        return panchayat_service.process_decision(listing_id, req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/analytics")
def get_panchayat_analytics():
    """
    Returns in-depth economic distribution, tourist flow redistribution, and community fund analytics.
    """
    return panchayat_service.get_analytics()
