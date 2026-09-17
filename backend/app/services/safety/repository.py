"""
Thread-safe Incident Repository & Retention Management for Yatri Setu (Milestone 7F).
Maintains in-memory state with thread-locks, idempotency lookups, and privacy retention scrubbing.
"""

import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.services.safety.schemas import (
    EmergencyIncident,
    IncidentStatus,
    IncidentSeverity,
    IncidentAuditRecord,
    NotificationRecord,
)


class SafetyIncidentRepository:
    """Thread-safe store for emergency incidents, audit trails, and idempotency indexing."""

    def __init__(self):
        self._lock = threading.Lock()
        self._incidents: Dict[str, EmergencyIncident] = {}
        self._idempotency_map: Dict[str, str] = {}  # idempotency_key -> incident_id
        self._phone_recent_map: Dict[str, str] = {}  # phone -> incident_id (for fast debounce)

    def save_incident(self, incident: EmergencyIncident) -> EmergencyIncident:
        with self._lock:
            self._incidents[incident.incident_id] = incident
            if incident.idempotency_key:
                self._idempotency_map[incident.idempotency_key] = incident.incident_id
            self._phone_recent_map[incident.user_phone] = incident.incident_id
        self._persist_incident(incident)
        return incident

    def _persist_incident(self, incident: EmergencyIncident) -> None:
        """Helper to synchronize EmergencyIncident state with SQLAlchemy model."""
        try:
            from app.core.database import SessionLocal
            from app.models.entities import SafetyIncidentModel

            lat = incident.location.latitude if incident.location else None
            lon = incident.location.longitude if incident.location else None
            audit_json = [a.model_dump() if hasattr(a, "model_dump") else (a.dict() if hasattr(a, "dict") else a.__dict__) for a in incident.audit_trail]
            notif_json = [n.model_dump() if hasattr(n, "model_dump") else (n.dict() if hasattr(n, "dict") else n.__dict__) for n in incident.notifications]

            db = SessionLocal()
            try:
                db_inc = db.query(SafetyIncidentModel).filter(SafetyIncidentModel.id == incident.incident_id).first()
                type_val = incident.incident_type.value if hasattr(incident.incident_type, "value") else str(incident.incident_type)
                sev_val = incident.severity.value if hasattr(incident.severity, "value") else str(incident.severity)
                stat_val = incident.status.value if hasattr(incident.status, "value") else str(incident.status)

                if not db_inc:
                    db_inc = SafetyIncidentModel(
                        id=incident.incident_id,
                        destination_id=incident.destination_id,
                        trip_id=incident.trip_id,
                        traveler_session_id=incident.traveler_session_id,
                        user_name=incident.user_name,
                        user_phone=incident.user_phone,
                        incident_type=type_val,
                        severity=sev_val,
                        status=stat_val,
                        notes=incident.notes,
                        description=incident.notes or f"SOS incident triggered for {incident.user_name}",
                        latitude=lat,
                        longitude=lon,
                        resolved=(incident.status == IncidentStatus.RESOLVED),
                        escalation_level=incident.escalation_level,
                        idempotency_key=incident.idempotency_key,
                        audit_trail_json=audit_json,
                        notifications_json=notif_json
                    )
                    db.add(db_inc)
                else:
                    db_inc.status = stat_val
                    db_inc.severity = sev_val
                    db_inc.notes = incident.notes
                    db_inc.resolved = (incident.status == IncidentStatus.RESOLVED)
                    db_inc.escalation_level = incident.escalation_level
                    db_inc.audit_trail_json = audit_json
                    db_inc.notifications_json = notif_json

                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        except Exception:
            pass

    def get_incident(self, incident_id: str) -> Optional[EmergencyIncident]:
        with self._lock:
            inc = self._incidents.get(incident_id)
            if inc:
                return inc

        # Fallback database hydration
        try:
            from app.core.database import SessionLocal
            from app.models.entities import SafetyIncidentModel
            from app.services.safety.schemas import LocationData, IncidentType, IncidentSeverity, IncidentStatus

            db = SessionLocal()
            try:
                db_inc = db.query(SafetyIncidentModel).filter(SafetyIncidentModel.id == incident_id).first()
                if db_inc:
                    loc = None
                    if db_inc.latitude is not None and db_inc.longitude is not None:
                        loc = LocationData(latitude=db_inc.latitude, longitude=db_inc.longitude)
                    hydrated = EmergencyIncident(
                        incident_id=db_inc.id,
                        trip_id=db_inc.trip_id,
                        traveler_session_id=db_inc.traveler_session_id,
                        destination_id=db_inc.destination_id,
                        location=loc,
                        incident_type=IncidentType(db_inc.incident_type) if db_inc.incident_type in IncidentType._value2member_map_ else IncidentType.SOS,
                        severity=IncidentSeverity(db_inc.severity) if db_inc.severity in IncidentSeverity._value2member_map_ else IncidentSeverity.HIGH,
                        status=IncidentStatus(db_inc.status) if db_inc.status in IncidentStatus._value2member_map_ else IncidentStatus.DELIVERED,
                        notes=db_inc.notes,
                        user_name=db_inc.user_name or "Tourist",
                        user_phone=db_inc.user_phone or "+91 98000 00000",
                        created_at=db_inc.timestamp.isoformat() if hasattr(db_inc.timestamp, "isoformat") else str(db_inc.timestamp),
                        escalation_level=db_inc.escalation_level or 0,
                        idempotency_key=db_inc.idempotency_key
                    )
                    with self._lock:
                        self._incidents[hydrated.incident_id] = hydrated
                        if hydrated.idempotency_key:
                            self._idempotency_map[hydrated.idempotency_key] = hydrated.incident_id
                    return hydrated
            finally:
                db.close()
        except Exception:
            pass
        return None

    def get_by_idempotency_key(self, key: str) -> Optional[EmergencyIncident]:
        with self._lock:
            inc_id = self._idempotency_map.get(key)
            if inc_id:
                return self._incidents.get(inc_id)
            return None

    def get_latest_by_phone(self, phone: str) -> Optional[EmergencyIncident]:
        with self._lock:
            inc_id = self._phone_recent_map.get(phone)
            if inc_id:
                return self._incidents.get(inc_id)
            return None

    def list_incidents(
        self,
        status: Optional[str] = None,
        destination_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[EmergencyIncident]:
        with self._lock:
            results = list(self._incidents.values())

            if status:
                st_upper = status.upper().strip()
                results = [i for i in results if i.status.value == st_upper]

            if destination_id:
                dest_lower = destination_id.lower().strip()
                results = [i for i in results if i.destination_id.lower() == dest_lower]

            if severity:
                sev_upper = severity.upper().strip()
                results = [i for i in results if i.severity.value == sev_upper]

            # Sort descending by created_at
            results.sort(key=lambda x: x.created_at, reverse=True)
            return results[:limit]

    def list_active_incidents(self) -> List[EmergencyIncident]:
        with self._lock:
            active_statuses = {
                IncidentStatus.CREATED,
                IncidentStatus.DELIVERY_PENDING,
                IncidentStatus.DELIVERED,
                IncidentStatus.ACKNOWLEDGED,
                IncidentStatus.RESPONDING,
                IncidentStatus.ESCALATED
            }
            results = [i for i in self._incidents.values() if i.status in active_statuses]
            results.sort(key=lambda x: (
                0 if x.severity == IncidentSeverity.CRITICAL else
                1 if x.severity == IncidentSeverity.HIGH else
                2 if x.severity == IncidentSeverity.MEDIUM else 3,
                x.created_at
            ))
            return results

    def add_audit_record(self, incident_id: str, record: IncidentAuditRecord):
        with self._lock:
            incident = self._incidents.get(incident_id)
            if incident:
                incident.audit_trail.append(record)
        if incident:
            self._persist_incident(incident)

    def add_notification_record(self, incident_id: str, record: NotificationRecord):
        with self._lock:
            incident = self._incidents.get(incident_id)
            if incident:
                incident.notifications.append(record)
        if incident:
            self._persist_incident(incident)

    def apply_retention_scrub(self, hours_threshold: int = 24) -> int:
        """
        Privacy policy compliance: scrubs raw GPS coordinates from resolved/cancelled
        incidents older than configured hours threshold.
        """
        scrubbed_count = 0
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=hours_threshold)

        with self._lock:
            for inc in self._incidents.values():
                if inc.status in (IncidentStatus.RESOLVED, IncidentStatus.CANCELLED):
                    end_time_str = inc.resolved_at or inc.cancelled_at or inc.created_at
                    try:
                        end_dt = datetime.fromisoformat(end_time_str.replace("Z", ""))
                    except Exception:
                        end_dt = now

                    if end_dt <= cutoff and inc.location and inc.location.latitude is not None:
                        inc.location.latitude = None
                        inc.location.longitude = None
                        inc.location.accuracy_m = None
                        inc.location.label = "REDACTED_PER_PRIVACY_RETENTION_POLICY"
                        scrubbed_count += 1

        return scrubbed_count

    def clear(self):
        """Resets the repository (for testing isolation)."""
        with self._lock:
            self._incidents.clear()
            self._idempotency_map.clear()
            self._phone_recent_map.clear()


safety_incident_repository = SafetyIncidentRepository()
