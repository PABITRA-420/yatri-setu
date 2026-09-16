"""
Pydantic Schemas and Enums for Safety, SOS & Emergency Operations (Milestone 7F).
Defines normalized incident models, deterministic state transitions, audit trails, and provenance.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class IncidentType(str, Enum):
    SOS = "SOS"
    MEDICAL = "MEDICAL"
    ACCIDENT = "ACCIDENT"
    LOST = "LOST"
    SECURITY = "SECURITY"
    WEATHER = "WEATHER"
    ROAD_BLOCKED = "ROAD_BLOCKED"
    OTHER = "OTHER"


class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    CREATED = "CREATED"
    DELIVERY_PENDING = "DELIVERY_PENDING"
    DELIVERED = "DELIVERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESPONDING = "RESPONDING"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class ProviderMode(str, Enum):
    DEMO = "DEMO"
    INTERNAL = "INTERNAL"
    REAL_EXTERNAL = "REAL_EXTERNAL"


class NotificationChannel(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    DELIVERED = "DELIVERED"


class DataQuality(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class SafetyProvenance(str, Enum):
    REAL_NETWORK = "REAL — YATRI SETU NETWORK"
    DEMO_SYNTHETIC = "DEMO — SYNTHETIC"
    REAL_EXTERNAL = "REAL EXTERNAL — INTEGRATION"
    UNAVAILABLE = "UNAVAILABLE"


class LocationData(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_m: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "AVAILABLE"  # AVAILABLE, UNAVAILABLE, APPROXIMATE
    label: Optional[str] = None


class RouteSafetyContext(BaseModel):
    corridor_name: Optional[str] = None
    corridor_access_status: str = "NORMAL"  # NORMAL, CAUTION, RESTRICTED, CLOSED
    severe_weather_alert: Optional[str] = None
    is_severe_weather: bool = False
    context_note: str = "Contextual corridor/weather telemetry only. No automatic causality inferred."


class IncidentAuditRecord(BaseModel):
    record_id: str
    incident_id: str
    timestamp: str
    actor: str  # e.g., "TOURIST", "OPERATOR:op_desk_1", "SYSTEM_ESCALATION_MONITOR"
    action: str  # "CREATED", "ACKNOWLEDGED", "RESPONDING", "ESCALATED", "RESOLVED", "CANCELLED", "DUPLICATE_SUPPRESSED"
    previous_state: Optional[str] = None
    new_state: str
    details: Optional[str] = None


class NotificationRecord(BaseModel):
    notification_id: str
    incident_id: str
    recipient_type: str  # "OPERATOR", "TOURIST", "EMERGENCY_DESK"
    channel: NotificationChannel = NotificationChannel.IN_APP
    status: NotificationStatus = NotificationStatus.DELIVERED
    sent_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    provider: str = "Internal In-App Notification Hub"
    provider_mode: ProviderMode = ProviderMode.INTERNAL
    details: Optional[str] = None


class OfficialEmergencyContact(BaseModel):
    service_name: str
    contact_number: str
    toll_free: bool
    region: str
    category: str
    verification_label: str = "OFFICIAL INFORMATION — VERIFIED PUBLIC SERVICE"


class ResponderInfo(BaseModel):
    name: str
    agency: str
    distance_km: float
    eta_minutes: int
    phone: str
    status: str  # "DISPATCHED", "STANDBY", "ACKNOWLEDGED"


class EmergencyIncident(BaseModel):
    incident_id: str
    trip_id: Optional[str] = None
    traveler_session_id: Optional[str] = None
    destination_id: str = "kalimpong"
    location: Optional[LocationData] = None
    incident_type: IncidentType = IncidentType.SOS
    severity: IncidentSeverity = IncidentSeverity.HIGH
    status: IncidentStatus = IncidentStatus.DELIVERED
    notes: Optional[str] = None
    user_name: str
    user_phone: str
    created_at: str
    delivered_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    responding_at: Optional[str] = None
    escalated_at: Optional[str] = None
    resolved_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    delivery_latency_seconds: Optional[float] = None
    acknowledgement_latency_seconds: Optional[float] = None
    assigned_operator: Optional[str] = None
    escalation_level: int = 0
    escalation_reason: Optional[str] = None
    source: str = "YATRI_SETU_TOURIST_APP"
    provider_mode: ProviderMode = ProviderMode.INTERNAL
    data_quality: DataQuality = DataQuality.HIGH
    provenance: str = SafetyProvenance.REAL_NETWORK.value
    repeat_count: int = 1
    idempotency_key: Optional[str] = None
    cancellation_reason: Optional[str] = None
    route_context: Optional[RouteSafetyContext] = None
    audit_trail: List[IncidentAuditRecord] = []
    notifications: List[NotificationRecord] = []


class SosTriggerRequest(BaseModel):
    user_name: str
    user_phone: str
    destination_id: Optional[str] = "kalimpong"
    trip_id: Optional[str] = None
    traveler_session_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_accuracy_m: Optional[float] = None
    current_location_name: Optional[str] = None
    incident_type: Optional[IncidentType] = IncidentType.SOS
    severity: Optional[IncidentSeverity] = IncidentSeverity.HIGH
    nature_of_emergency: Optional[str] = None
    notes: Optional[str] = None
    idempotency_key: Optional[str] = None
    client_timestamp: Optional[str] = None
    offline_queued: bool = False


class SosCancelRequest(BaseModel):
    reason: Optional[str] = "Accidental tap"
    cancelled_by: Optional[str] = "TOURIST"


class IncidentActionRequest(BaseModel):
    operator_id: str = "operator_desk_1"
    notes: Optional[str] = None
    escalation_reason: Optional[str] = None


class EmergencyOperationsSummary(BaseModel):
    total_active: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    awaiting_acknowledgement_count: int
    escalation_required_count: int
    resolved_today_count: int
    avg_acknowledgement_latency_seconds: Optional[float] = None
    incidents: List[EmergencyIncident] = []


class SosFullResponse(BaseModel):
    """Backward-compatible + extended response for SOS trigger."""
    # Existing M1-M5 compatibility fields:
    alert_id: str
    status: str
    timestamp: str
    user_name: str
    user_phone: str
    gps_coordinates: str
    nearest_responders: List[ResponderInfo]
    national_helplines: List[dict]
    instructions_for_traveler: List[str]
    beacon_signal_strength: str

    # Milestone 7F extended incident fields:
    incident: EmergencyIncident
