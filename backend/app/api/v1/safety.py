from fastapi import APIRouter
from app.models.safety import SosAlertRequest, SosAlertResponse
from app.services.safety_service import trigger_sos_alert

router = APIRouter(prefix="/safety", tags=["Traveler Safety & SOS"])

@router.post("/sos", response_model=SosAlertResponse)
def trigger_sos(request: SosAlertRequest):
    """
    Emergency SOS trigger.
    Simulates instantaneous distress broadcast, transmits GPS coordinates,
    and alerts the nearest local police, hospital, and Yatri Mitra volunteer responders.
    """
    return trigger_sos_alert(request)
