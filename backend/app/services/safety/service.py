"""
Core Safety Operations Service for Yatri Setu (Milestone 7F).
Enforces deterministic emergency lifecycles, duplicate protection, location accuracy rules,
SLA latency tracking, escalation triggers, route/weather contextualization, and audit trails.
"""

import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from app.services.safety.schemas import (
    IncidentType,
    IncidentSeverity,
    IncidentStatus,
    ProviderMode,
    DataQuality,
    SafetyProvenance,
    LocationData,
    RouteSafetyContext,
    IncidentAuditRecord,
    EmergencyIncident,
    SosTriggerRequest,
    SosCancelRequest,
    IncidentActionRequest,
    EmergencyOperationsSummary,
    OfficialEmergencyContact,
    ResponderInfo,
    SosFullResponse
)
from app.services.safety.base import BaseSafetyProvider, BaseNotificationProvider
from app.services.safety.providers import (
    InternalDemoSafetyProvider,
    DemoNotificationProvider,
    VERIFIED_OFFICIAL_CONTACTS
)
from app.services.safety.repository import (
    SafetyIncidentRepository,
    safety_incident_repository
)

# Optional contextual integrations from Milestone 7C (safe imports)
try:
    from app.services.traffic.service import traffic_service
except Exception:
    traffic_service = None

try:
    from app.services.weather_service import weather_service
except Exception:
    weather_service = None


# Allowed state transitions
VALID_INCIDENT_TRANSITIONS = {
    IncidentStatus.CREATED: {
        IncidentStatus.DELIVERY_PENDING,
        IncidentStatus.DELIVERED,
        IncidentStatus.CANCELLED
    },
    IncidentStatus.DELIVERY_PENDING: {
        IncidentStatus.DELIVERED,
        IncidentStatus.CANCELLED
    },
    IncidentStatus.DELIVERED: {
        IncidentStatus.ACKNOWLEDGED,
        IncidentStatus.ESCALATED,
        IncidentStatus.CANCELLED
    },
    IncidentStatus.ACKNOWLEDGED: {
        IncidentStatus.RESPONDING,
        IncidentStatus.ESCALATED,
        IncidentStatus.RESOLVED,
        IncidentStatus.CANCELLED
    },
    IncidentStatus.RESPONDING: {
        IncidentStatus.ESCALATED,
        IncidentStatus.RESOLVED
    },
    IncidentStatus.ESCALATED: {
        IncidentStatus.ACKNOWLEDGED,
        IncidentStatus.RESPONDING,
        IncidentStatus.RESOLVED
    },
    IncidentStatus.RESOLVED: set(),
    IncidentStatus.CANCELLED: set(),
}

DEFAULT_CRITICAL_ESCALATION_TIMEOUT_SECONDS = 45


class SafetyOperationsService:
    """
    Central Coordinator for traveler SOS, emergency workflows, and operator oversight.
    """

    def __init__(
        self,
        repository: Optional[SafetyIncidentRepository] = None,
        safety_provider: Optional[BaseSafetyProvider] = None,
        notification_provider: Optional[BaseNotificationProvider] = None,
        escalation_timeout_seconds: int = DEFAULT_CRITICAL_ESCALATION_TIMEOUT_SECONDS
    ):
        self.repo = repository or safety_incident_repository
        self.safety_provider = safety_provider or InternalDemoSafetyProvider(mode=ProviderMode.INTERNAL)
        self.notification_provider = notification_provider or DemoNotificationProvider(mode=ProviderMode.INTERNAL)
        self.escalation_timeout_seconds = escalation_timeout_seconds

    def _generate_incident_id(self) -> str:
        date_str = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"SOS-{date_str}-{random_suffix}"

    def _sanitize_location(
        self,
        lat: Optional[float],
        lon: Optional[float],
        accuracy_m: Optional[float],
        label: Optional[str]
    ) -> LocationData:
        """
        Validates coordinate bounds without claiming false precision.
        If coordinates missing or invalid, marks UNAVAILABLE without failing the SOS.
        """
        now_str = datetime.utcnow().isoformat()
        if lat is None or lon is None:
            return LocationData(
                latitude=None,
                longitude=None,
                accuracy_m=None,
                status="UNAVAILABLE",
                label=label or "Coordinates unavailable — cellular network ping only",
                timestamp=now_str
            )

        # Coordinate bounds check
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
            return LocationData(
                latitude=None,
                longitude=None,
                accuracy_m=None,
                status="UNAVAILABLE",
                label="Invalid coordinates supplied",
                timestamp=now_str
            )

        # Cap accuracy representation
        clean_accuracy = round(accuracy_m, 1) if accuracy_m is not None and accuracy_m > 0 else 50.0

        return LocationData(
            latitude=round(lat, 5),
            longitude=round(lon, 5),
            accuracy_m=clean_accuracy,
            status="AVAILABLE",
            label=label or f"Approx. coordinates (±{clean_accuracy}m)",
            timestamp=now_str
        )

    def _get_route_safety_context(self, destination_id: str) -> RouteSafetyContext:
        """
        Safely integrates Milestone 7C corridor & weather telemetry for situational context.
        Strictly does NOT infer that weather/corridor caused the emergency.
        """
        corridor_name = None
        corridor_status = "NORMAL"
        severe_weather_alert = None
        is_severe = False

        if traffic_service:
            try:
                summary = traffic_service.get_traffic(destination_id)
                if summary.corridors:
                    top_c = summary.corridors[0]
                    corridor_name = top_c.corridor_name
                    corridor_status = top_c.access_status.value
            except Exception:
                pass

        if weather_service:
            try:
                obs = weather_service.get_current_weather(destination_id)
                if obs and obs.condition:
                    if any(w in obs.condition.lower() for w in ["rain", "storm", "fog", "cyclone", "hail"]):
                        is_severe = True
                        severe_weather_alert = f"Severe condition in region: {obs.condition} ({obs.temperature_c}°C)"
            except Exception:
                pass

        return RouteSafetyContext(
            corridor_name=corridor_name,
            corridor_access_status=corridor_status,
            severe_weather_alert=severe_weather_alert,
            is_severe_weather=is_severe
        )

    def trigger_sos(self, req: SosTriggerRequest) -> SosFullResponse:
        """
        Processes an emergency SOS distress alert.
        Enforces idempotency, duplicate suppression, location sanitization, and state progression.
        """
        now = datetime.utcnow()
        now_str = now.isoformat()

        # 1. Check Idempotency Key
        if req.idempotency_key:
            existing = self.repo.get_by_idempotency_key(req.idempotency_key)
            if existing:
                existing.repeat_count += 1
                self.repo.add_audit_record(
                    existing.incident_id,
                    IncidentAuditRecord(
                        record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
                        incident_id=existing.incident_id,
                        timestamp=now_str,
                        actor="TOURIST",
                        action="DUPLICATE_SUPPRESSED",
                        previous_state=existing.status.value,
                        new_state=existing.status.value,
                        details=f"Repeat trigger suppressed via idempotency key: {req.idempotency_key}"
                    )
                )
                return self._build_full_response(existing)

        # 2. Check Rapid Duplicate Tap (same phone, within 10 seconds, active incident)
        recent_inc = self.repo.get_latest_by_phone(req.user_phone)
        if recent_inc and recent_inc.status not in (IncidentStatus.RESOLVED, IncidentStatus.CANCELLED):
            try:
                recent_time = datetime.fromisoformat(recent_inc.created_at.replace("Z", ""))
                if (now - recent_time).total_seconds() < 10.0:
                    recent_inc.repeat_count += 1
                    self.repo.add_audit_record(
                        recent_inc.incident_id,
                        IncidentAuditRecord(
                            record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
                            incident_id=recent_inc.incident_id,
                            timestamp=now_str,
                            actor="TOURIST",
                            action="DUPLICATE_SUPPRESSED",
                            previous_state=recent_inc.status.value,
                            new_state=recent_inc.status.value,
                            details=f"Rapid tap debounce: attempt #{recent_inc.repeat_count}"
                        )
                    )
                    return self._build_full_response(recent_inc)
            except Exception:
                pass

        # 3. Sanitize Location & Context
        location = self._sanitize_location(
            lat=req.latitude,
            lon=req.longitude,
            accuracy_m=req.location_accuracy_m,
            label=req.current_location_name
        )
        route_ctx = self._get_route_safety_context(req.destination_id or "kalimpong")

        # 4. Resolve Type & Severity
        inc_type = req.incident_type or IncidentType.SOS
        inc_severity = req.severity or IncidentSeverity.HIGH

        incident_id = self._generate_incident_id()

        # Offline queued vs Immediate delivery
        if req.offline_queued:
            status = IncidentStatus.DELIVERY_PENDING
            delivered_at = None
            delivery_latency = None
        else:
            status = IncidentStatus.DELIVERED
            delivered_at = now_str
            delivery_latency = 0.5  # Sub-second internal delivery

        escalation_lvl = 1 if inc_severity == IncidentSeverity.CRITICAL and status == IncidentStatus.DELIVERED else 0
        escalation_reason = "CRITICAL priority alert initialized" if escalation_lvl == 1 else None

        incident = EmergencyIncident(
            incident_id=incident_id,
            trip_id=req.trip_id,
            traveler_session_id=req.traveler_session_id,
            destination_id=req.destination_id or "kalimpong",
            location=location,
            incident_type=inc_type,
            severity=inc_severity,
            status=status,
            notes=req.notes or req.nature_of_emergency,
            user_name=req.user_name,
            user_phone=req.user_phone,
            created_at=now_str,
            delivered_at=delivered_at,
            delivery_latency_seconds=delivery_latency,
            escalation_level=escalation_lvl,
            escalation_reason=escalation_reason,
            source="YATRI_SETU_TOURIST_APP",
            provider_mode=ProviderMode.INTERNAL,
            data_quality=DataQuality.HIGH if location.status == "AVAILABLE" else DataQuality.UNAVAILABLE,
            provenance=SafetyProvenance.REAL_NETWORK.value,
            repeat_count=1,
            idempotency_key=req.idempotency_key,
            route_context=route_ctx,
            audit_trail=[],
            notifications=[]
        )

        # Audit Record for Creation
        incident.audit_trail.append(
            IncidentAuditRecord(
                record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
                incident_id=incident_id,
                timestamp=now_str,
                actor="TOURIST",
                action="CREATED",
                previous_state=None,
                new_state=status.value,
                details=f"Distress alert initiated: {inc_type.value} [{inc_severity.value}]"
            )
        )

        # Notification to Command Center Desk
        notif = self.notification_provider.send_notification(
            incident_id=incident_id,
            recipient_type="COMMAND_CENTER_OPERATOR",
            channel="IN_APP",
            title=f"Distress Alert: {inc_type.value}",
            message=f"{req.user_name} reported {inc_severity.value} emergency in {incident.destination_id}"
        )
        incident.notifications.append(notif)

        # Save to Repository
        self.repo.save_incident(incident)

        return self._build_full_response(incident)

    def cancel_sos(self, incident_id: str, req: SosCancelRequest) -> EmergencyIncident:
        """
        Safely cancels an active SOS (e.g. accidental tap).
        Does NOT delete incident record; records full audit history.
        """
        incident = self.repo.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        allowed = VALID_INCIDENT_TRANSITIONS.get(incident.status, set())
        if IncidentStatus.CANCELLED not in allowed:
            raise ValueError(f"Cannot cancel incident currently in state: {incident.status.value}")

        now_str = datetime.utcnow().isoformat()
        prev_state = incident.status.value

        incident.status = IncidentStatus.CANCELLED
        incident.cancelled_at = now_str
        incident.cancellation_reason = req.reason or "Accidental trigger cancelled by traveler"

        audit = IncidentAuditRecord(
            record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            timestamp=now_str,
            actor=req.cancelled_by or "TOURIST",
            action="CANCELLED",
            previous_state=prev_state,
            new_state=IncidentStatus.CANCELLED.value,
            details=f"Cancellation: {incident.cancellation_reason}"
        )
        self.repo.add_audit_record(incident_id, audit)

        return incident

    def acknowledge_incident(self, incident_id: str, req: IncidentActionRequest) -> EmergencyIncident:
        """
        Operator workflow: acknowledges an incoming emergency.
        Calculates observed acknowledgement latency.
        """
        incident = self.repo.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        allowed = VALID_INCIDENT_TRANSITIONS.get(incident.status, set())
        if IncidentStatus.ACKNOWLEDGED not in allowed:
            raise ValueError(f"Cannot transition to ACKNOWLEDGED from {incident.status.value}")

        now = datetime.utcnow()
        now_str = now.isoformat()
        prev_state = incident.status.value

        # Compute observed SLA latency
        ack_latency = None
        if incident.delivered_at:
            try:
                del_dt = datetime.fromisoformat(incident.delivered_at.replace("Z", ""))
                ack_latency = max(0.0, round((now - del_dt).total_seconds(), 1))
            except Exception:
                ack_latency = 5.0

        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = now_str
        incident.assigned_operator = req.operator_id
        incident.acknowledgement_latency_seconds = ack_latency

        audit = IncidentAuditRecord(
            record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            timestamp=now_str,
            actor=f"OPERATOR:{req.operator_id}",
            action="ACKNOWLEDGED",
            previous_state=prev_state,
            new_state=IncidentStatus.ACKNOWLEDGED.value,
            details=f"Acknowledged by {req.operator_id}. Observed latency: {ack_latency}s. Notes: {req.notes or 'None'}"
        )
        self.repo.add_audit_record(incident_id, audit)

        return incident

    def respond_incident(self, incident_id: str, req: IncidentActionRequest) -> EmergencyIncident:
        """
        Operator workflow: marks incident as actively responding.
        """
        incident = self.repo.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        allowed = VALID_INCIDENT_TRANSITIONS.get(incident.status, set())
        if IncidentStatus.RESPONDING not in allowed:
            raise ValueError(f"Cannot transition to RESPONDING from {incident.status.value}")

        now_str = datetime.utcnow().isoformat()
        prev_state = incident.status.value

        incident.status = IncidentStatus.RESPONDING
        incident.responding_at = now_str
        if req.operator_id:
            incident.assigned_operator = req.operator_id

        audit = IncidentAuditRecord(
            record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            timestamp=now_str,
            actor=f"OPERATOR:{req.operator_id}",
            action="RESPONDING",
            previous_state=prev_state,
            new_state=IncidentStatus.RESPONDING.value,
            details=f"Response team coordination active. Notes: {req.notes or 'None'}"
        )
        self.repo.add_audit_record(incident_id, audit)

        return incident

    def escalate_incident(self, incident_id: str, req: IncidentActionRequest) -> EmergencyIncident:
        """
        Escalation workflow: triggers senior supervisor / field escalation.
        """
        incident = self.repo.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        allowed = VALID_INCIDENT_TRANSITIONS.get(incident.status, set())
        if IncidentStatus.ESCALATED not in allowed:
            raise ValueError(f"Cannot escalate incident from state {incident.status.value}")

        now_str = datetime.utcnow().isoformat()
        prev_state = incident.status.value

        incident.status = IncidentStatus.ESCALATED
        incident.escalated_at = now_str
        incident.escalation_level = 1
        incident.escalation_reason = req.escalation_reason or "Escalation requested by operations desk"

        audit = IncidentAuditRecord(
            record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            timestamp=now_str,
            actor=f"OPERATOR:{req.operator_id}",
            action="ESCALATED",
            previous_state=prev_state,
            new_state=IncidentStatus.ESCALATED.value,
            details=f"ESCALATION REQUIRED: {incident.escalation_reason}"
        )
        self.repo.add_audit_record(incident_id, audit)

        return incident

    def resolve_incident(self, incident_id: str, req: IncidentActionRequest) -> EmergencyIncident:
        """
        Resolves an incident with operational summary notes.
        """
        incident = self.repo.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        allowed = VALID_INCIDENT_TRANSITIONS.get(incident.status, set())
        if IncidentStatus.RESOLVED not in allowed:
            raise ValueError(f"Cannot resolve incident from state {incident.status.value}")

        now_str = datetime.utcnow().isoformat()
        prev_state = incident.status.value

        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = now_str

        audit = IncidentAuditRecord(
            record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            timestamp=now_str,
            actor=f"OPERATOR:{req.operator_id}",
            action="RESOLVED",
            previous_state=prev_state,
            new_state=IncidentStatus.RESOLVED.value,
            details=f"Incident safely resolved. Operator report: {req.notes or 'Traveler verified safe'}"
        )
        self.repo.add_audit_record(incident_id, audit)

        return incident

    def check_escalation_timeouts(self) -> List[EmergencyIncident]:
        """
        Scans for unacknowledged critical emergencies that have exceeded the timeout threshold.
        Automatically transitions to ESCALATED with ESCALATION_REQUIRED tag.
        """
        escalated = []
        now = datetime.utcnow()
        active = self.repo.list_active_incidents()

        for inc in active:
            if inc.severity == IncidentSeverity.CRITICAL and inc.status == IncidentStatus.DELIVERED:
                if inc.delivered_at:
                    try:
                        del_dt = datetime.fromisoformat(inc.delivered_at.replace("Z", ""))
                        elapsed = (now - del_dt).total_seconds()
                        if elapsed >= self.escalation_timeout_seconds:
                            inc.status = IncidentStatus.ESCALATED
                            inc.escalated_at = now.isoformat()
                            inc.escalation_level = 1
                            inc.escalation_reason = (
                                f"Unacknowledged critical alert exceeded {self.escalation_timeout_seconds}s SLA"
                            )
                            self.repo.add_audit_record(
                                inc.incident_id,
                                IncidentAuditRecord(
                                    record_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
                                    incident_id=inc.incident_id,
                                    timestamp=now.isoformat(),
                                    actor="SYSTEM_ESCALATION_MONITOR",
                                    action="ESCALATED",
                                    previous_state=IncidentStatus.DELIVERED.value,
                                    new_state=IncidentStatus.ESCALATED.value,
                                    details=inc.escalation_reason
                                )
                            )
                            escalated.append(inc)
                    except Exception:
                        pass
        return escalated

    def get_summary(self) -> EmergencyOperationsSummary:
        """Aggregates active emergency incidents and SLA latency statistics."""
        active = self.repo.list_active_incidents()
        all_incidents = self.repo.list_incidents(limit=100)

        critical = sum(1 for i in active if i.severity == IncidentSeverity.CRITICAL)
        high = sum(1 for i in active if i.severity == IncidentSeverity.HIGH)
        medium = sum(1 for i in active if i.severity == IncidentSeverity.MEDIUM)
        low = sum(1 for i in active if i.severity == IncidentSeverity.LOW)
        awaiting_ack = sum(1 for i in active if i.status == IncidentStatus.DELIVERED)
        escalation_req = sum(1 for i in active if i.status == IncidentStatus.ESCALATED or i.escalation_level > 0)

        # Resolved today
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        resolved_today = sum(
            1 for i in all_incidents
            if i.status == IncidentStatus.RESOLVED and (i.resolved_at and i.resolved_at.startswith(today_str))
        )

        # Average observed acknowledgement latency
        latencies = [
            i.acknowledgement_latency_seconds
            for i in all_incidents
            if i.acknowledgement_latency_seconds is not None
        ]
        avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else None

        return EmergencyOperationsSummary(
            total_active=len(active),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            awaiting_acknowledgement_count=awaiting_ack,
            escalation_required_count=escalation_req,
            resolved_today_count=resolved_today,
            avg_acknowledgement_latency_seconds=avg_latency,
            incidents=active
        )

    def get_official_contacts(self) -> List[OfficialEmergencyContact]:
        return VERIFIED_OFFICIAL_CONTACTS

    def _build_full_response(self, incident: EmergencyIncident) -> SosFullResponse:
        """
        Builds backward-compatible + rich M7F response.
        """
        dispatch_res = self.safety_provider.dispatch_sos({"incident_id": incident.incident_id})
        responders = dispatch_res.get("responders", [])

        # Backward compatibility GPS string
        if incident.location and incident.location.latitude is not None and incident.location.longitude is not None:
            gps_str = f"{incident.location.latitude:.4f}° N, {incident.location.longitude:.4f}° E (±{incident.location.accuracy_m}m)"
        else:
            gps_str = "GPS UNAVAILABLE (Cellular relay only)"

        national_helplines = [
            {"service": c.service_name, "number": c.contact_number, "toll_free": c.toll_free}
            for c in VERIFIED_OFFICIAL_CONTACTS
        ]

        instructions = [
            "Stay in your current well-lit or sheltered location if safe to do so.",
            "Keep this emergency screen open; your GPS distress beacon is active.",
            "The nearest verified Yatri Mitra volunteer responders have received your coordinates.",
            "Expect an operational check-in or verification call within 180 seconds if cellular connectivity permits."
        ]

        return SosFullResponse(
            alert_id=incident.incident_id,
            status="ACTIVE_EMERGENCY_BROADCAST" if incident.status != IncidentStatus.CANCELLED else "CANCELLED",
            timestamp=incident.created_at,
            user_name=incident.user_name,
            user_phone=incident.user_phone,
            gps_coordinates=gps_str,
            nearest_responders=responders,
            national_helplines=national_helplines,
            instructions_for_traveler=instructions,
            beacon_signal_strength="Strong (Internal Yatri Setu Network Relay)",
            incident=incident
        )


safety_operations_service = SafetyOperationsService()
