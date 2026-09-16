from typing import List
from app.models.safety import SosAlertRequest, SosAlertResponse, ResponderInfo
from app.data.seed_data import EMERGENCY_RESPONDERS
from app.services.safety.schemas import (
    SosTriggerRequest,
    IncidentType,
    IncidentSeverity
)
from app.services.safety.service import safety_operations_service

NATIONAL_HELPLINES = [
    {"service": "National Emergency Number", "number": "112", "toll_free": True},
    {"service": "Tourist Safety Helpline", "number": "1363", "toll_free": True},
    {"service": "Women Helpline", "number": "1091", "toll_free": True},
    {"service": "Disaster Management Control Room", "number": "1070", "toll_free": True},
    {"service": "Himalayan Mountain Rescue Service", "number": "+91 3552 255100", "toll_free": False}
]

INSTRUCTIONS_FOR_TRAVELER = [
    "Stay in your current well-lit or sheltered location if safe to do so.",
    "Keep this emergency screen open; your GPS beacon is transmitting in real time.",
    "The nearest rural volunteer (Yatri Mitra) has received your distress ping and coordinates.",
    "If you have mobile signal, expect a verification call from the Sub-Divisional Police control desk within 180 seconds."
]

def trigger_sos_alert(req: SosAlertRequest) -> SosAlertResponse:
    """
    Processes an SOS distress broadcast via Milestone 7F Safety Operations Service.
    Enforces normalized incident creation, idempotency, duplicate suppression, and audit logging.
    """
    # Parse incident type enum safely
    inc_type = IncidentType.SOS
    if req.incident_type:
        try:
            inc_type = IncidentType(req.incident_type.upper())
        except Exception:
            pass

    # Parse severity enum safely
    inc_sev = IncidentSeverity.HIGH
    if req.severity:
        try:
            inc_sev = IncidentSeverity(req.severity.upper())
        except Exception:
            pass

    trigger_req = SosTriggerRequest(
        user_name=req.user_name,
        user_phone=req.user_phone,
        destination_id=req.destination_id,
        trip_id=req.trip_id,
        traveler_session_id=req.traveler_session_id,
        current_location_name=req.current_location_name,
        latitude=req.latitude,
        longitude=req.longitude,
        location_accuracy_m=req.location_accuracy_m,
        incident_type=inc_type,
        severity=inc_sev,
        nature_of_emergency=req.nature_of_emergency,
        notes=req.notes,
        idempotency_key=req.idempotency_key,
        offline_queued=req.offline_queued or False
    )

    full_res = safety_operations_service.trigger_sos(trigger_req)

    def _to_dict(obj):
        return obj.model_dump() if hasattr(obj, "model_dump") else obj.dict()

    # Convert to SosAlertResponse for strict backward compatibility
    responders = [ResponderInfo(**_to_dict(r)) for r in full_res.nearest_responders]

    return SosAlertResponse(
        alert_id=full_res.alert_id,
        status=full_res.status,
        timestamp=full_res.timestamp,
        user_name=full_res.user_name,
        user_phone=full_res.user_phone,
        gps_coordinates=full_res.gps_coordinates,
        nearest_responders=responders,
        national_helplines=full_res.national_helplines,
        instructions_for_traveler=full_res.instructions_for_traveler,
        beacon_signal_strength=full_res.beacon_signal_strength,
        incident=_to_dict(full_res.incident)
    )


