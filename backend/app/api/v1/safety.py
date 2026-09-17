from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, Depends
from app.models.safety import SosAlertRequest, SosAlertResponse
from app.services.safety_service import trigger_sos_alert
from app.services.safety.schemas import (
    SosCancelRequest,
    EmergencyIncident,
    OfficialEmergencyContact
)
from app.services.safety.service import safety_operations_service
from app.core.rate_limit import sos_rate_limiter

router = APIRouter(prefix="/safety", tags=["Traveler Safety & SOS"])

@router.post("/sos", response_model=SosAlertResponse, dependencies=[Depends(sos_rate_limiter.check_rate_limit)])
def trigger_sos(request: SosAlertRequest):
    """
    Emergency SOS trigger.
    Processes distress broadcast, registers incident with deterministic state machine,
    evaluates route/weather context, and alerts local Yatri Mitra volunteer coordinators.
    """
    return trigger_sos_alert(request)


@router.post("/sos/{incident_id}/cancel", response_model=EmergencyIncident)
def cancel_sos(
    incident_id: str = Path(..., description="ID of the SOS incident to cancel"),
    request: Optional[SosCancelRequest] = None
):
    """
    Cancel an accidental SOS activation.
    Preserves audit history and prevents ghost emergency dispatches.
    """
    req = request or SosCancelRequest(reason="Accidental activation cancelled by traveler")
    try:
        return safety_operations_service.cancel_sos(incident_id, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sos/{incident_id}/status", response_model=EmergencyIncident)
def get_sos_status(
    incident_id: str = Path(..., description="Incident ID to check status for")
):
    """
    Tourist-facing status tracker.
    Returns current progression: DELIVERED -> ACKNOWLEDGED -> RESPONDING -> RESOLVED.
    """
    inc = safety_operations_service.repo.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Emergency incident not found")
    return inc


@router.get("/contacts", response_model=List[OfficialEmergencyContact])
def list_official_contacts():
    """
    Verified public emergency helplines directory.
    Stands as official information layer (112, 1363, 1091, 1070, Mountain Rescue).
    """
    return safety_operations_service.get_official_contacts()

