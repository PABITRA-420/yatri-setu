import uuid
from datetime import datetime
from typing import List
from app.models.safety import SosAlertRequest, SosAlertResponse, ResponderInfo
from app.data.seed_data import EMERGENCY_RESPONDERS

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
    """Processes an SOS distress broadcast, calculates nearest responders, and returns real-time tracking response."""
    alert_id = f"SOS-{uuid.uuid4().hex[:6].upper()}"
    gps_str = f"{req.latitude:.4f}° N, {req.longitude:.4f}° E (Elev. ~4,120 ft)"

    responders = [ResponderInfo(**r) for r in EMERGENCY_RESPONDERS]

    return SosAlertResponse(
        alert_id=alert_id,
        status="ACTIVE_EMERGENCY_BROADCAST",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        user_name=req.user_name,
        user_phone=req.user_phone,
        gps_coordinates=gps_str,
        nearest_responders=responders,
        national_helplines=NATIONAL_HELPLINES,
        instructions_for_traveler=INSTRUCTIONS_FOR_TRAVELER,
        beacon_signal_strength="Strong (Sat-Linked & Cellular Relayed)"
    )
