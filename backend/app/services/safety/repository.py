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
            return incident

    def get_incident(self, incident_id: str) -> Optional[EmergencyIncident]:
        with self._lock:
            return self._incidents.get(incident_id)

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

    def add_notification_record(self, incident_id: str, record: NotificationRecord):
        with self._lock:
            incident = self._incidents.get(incident_id)
            if incident:
                incident.notifications.append(record)

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
