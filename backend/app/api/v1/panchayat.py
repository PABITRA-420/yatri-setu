from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.models.panchayat import (
    PanchayatDashboard, PanchayatVerificationItem, PanchayatDecisionRequest,
    PanchayatDecisionResponse
)
from app.services.panchayat_service import panchayat_service

router = APIRouter(prefix="/panchayat", tags=["Gram Panchayat Administration"])

@router.get("/dashboard", response_model=PanchayatDashboard)
def get_panchayat_dashboard():
    """
    Returns administrative overview for Gram Panchayat Nodal Desk.
    Includes verified homestays, queue length, community fund reserves, and pressure relief index.
    """
    return panchayat_service.get_dashboard()

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
