from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ResponderInfo(BaseModel):
    name: str
    agency: str # e.g. "Kalimpong Sub-Division Police", "Neora Valley Forest Post", "Yatri Setu Rural Mitra Network"
    distance_km: float
    eta_minutes: int
    phone: str
    status: str # "DISPATCHED", "STANDBY", "ACKNOWLEDGED"

class SosAlertRequest(BaseModel):
    user_name: str
    user_phone: str
    destination_id: Optional[str] = "kalimpong"
    trip_id: Optional[str] = None
    traveler_session_id: Optional[str] = None
    current_location_name: Optional[str] = "Upper Cart Road, Kalimpong"
    latitude: Optional[float] = Field(27.0667, description="Current GPS Latitude")
    longitude: Optional[float] = Field(88.4667, description="Current GPS Longitude")
    location_accuracy_m: Optional[float] = None
    battery_level_percent: Optional[int] = 84
    nature_of_emergency: Optional[str] = Field("General Assistance / Medical / Route Lost", description="Category")
    incident_type: Optional[str] = "SOS"
    severity: Optional[str] = "HIGH"
    notes: Optional[str] = None
    idempotency_key: Optional[str] = None
    offline_queued: Optional[bool] = False

class SosAlertResponse(BaseModel):
    alert_id: str
    status: str # "ACTIVE_EMERGENCY_BROADCAST"
    timestamp: str
    user_name: str
    user_phone: str
    gps_coordinates: str
    nearest_responders: List[ResponderInfo]
    national_helplines: List[dict]
    instructions_for_traveler: List[str]
    beacon_signal_strength: str
    incident: Optional[Dict[str, Any]] = None

