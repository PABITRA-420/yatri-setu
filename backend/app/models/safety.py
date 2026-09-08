from typing import List, Optional
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
    current_location_name: Optional[str] = "Upper Cart Road, Kalimpong"
    latitude: float = Field(27.0667, description="Current GPS Latitude")
    longitude: float = Field(88.4667, description="Current GPS Longitude")
    battery_level_percent: Optional[int] = 84
    nature_of_emergency: str = Field("General Assistance / Medical / Route Lost", description="Category")
    notes: Optional[str] = None

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
