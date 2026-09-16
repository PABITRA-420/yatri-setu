"""
Comprehensive Test Suite for Milestone 7F: Safety, SOS & Emergency Operations Layer.
Verifies normalized incident schema, deterministic state machine, idempotency,
duplicate tap suppression, location validation, operator workflows, escalation timeouts,
retention scrubbing, route context, and regression safety across M1-M7E.
"""

import time
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.services.safety.schemas import (
    IncidentType,
    IncidentSeverity,
    IncidentStatus,
    SosTriggerRequest,
    SosCancelRequest,
    IncidentActionRequest,
    SafetyProvenance
)
from app.services.safety.service import safety_operations_service
from app.services.safety.repository import safety_incident_repository

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_safety_repo():
    """Ensure a clean repository before each test."""
    safety_incident_repository.clear()
    yield
    safety_incident_repository.clear()


class TestSosCreationAndLocation:
    def test_sos_creation_with_valid_gps(self):
        payload = {
            "user_name": "Tenzing Norgay",
            "user_phone": "+91 98000 11111",
            "destination_id": "darjeeling",
            "latitude": 27.0360,
            "longitude": 88.2627,
            "location_accuracy_m": 25.0,
            "incident_type": "SOS",
            "severity": "HIGH",
            "nature_of_emergency": "Stuck in heavy fog near Tiger Hill",
            "notes": "Battery low, staying near trail marker 4"
        }
        res = client.post("/api/safety/sos", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ACTIVE_EMERGENCY_BROADCAST"
        assert "incident" in data
        inc = data["incident"]
        assert inc["status"] == "DELIVERED"
        assert inc["severity"] == "HIGH"
        assert inc["location"]["status"] == "AVAILABLE"
        assert inc["location"]["latitude"] == 27.036
        assert inc["location"]["longitude"] == 88.2627
        assert inc["location"]["accuracy_m"] == 25.0
        assert len(inc["audit_trail"]) >= 1
        assert inc["audit_trail"][0]["action"] == "CREATED"

    def test_sos_creation_without_location_succeeds(self):
        """Mandatory requirement: SOS must succeed even when GPS coordinates are unavailable."""
        payload = {
            "user_name": "Priya Sharma",
            "user_phone": "+91 98000 22222",
            "destination_id": "kalimpong",
            "latitude": None,
            "longitude": None,
            "nature_of_emergency": "Lost trail, phone GPS permission denied"
        }
        res = client.post("/api/safety/sos", json=payload)
        assert res.status_code == 200
        data = res.json()
        inc = data["incident"]
        assert inc["status"] == "DELIVERED"
        assert inc["location"]["status"] == "UNAVAILABLE"
        assert inc["location"]["latitude"] is None
        assert inc["location"]["longitude"] is None
        assert "UNAVAILABLE" in data["gps_coordinates"]

    def test_sos_creation_invalid_coordinates_handled_gracefully(self):
        """Out of bounds coordinates (-999, 999) must be marked UNAVAILABLE without 500 error."""
        payload = {
            "user_name": "Rohan Sen",
            "user_phone": "+91 98000 33333",
            "latitude": 150.0,  # Invalid latitude (> 90)
            "longitude": 200.0,  # Invalid longitude (> 180)
            "nature_of_emergency": "Testing invalid GPS bounds"
        }
        res = client.post("/api/safety/sos", json=payload)
        assert res.status_code == 200
        inc = res.json()["incident"]
        assert inc["location"]["status"] == "UNAVAILABLE"
        assert inc["location"]["latitude"] is None


class TestDuplicateProtectionAndIdempotency:
    def test_idempotency_key_suppresses_duplicate_incidents(self):
        key = "IDEM-TEST-12345"
        payload = {
            "user_name": "Aarav Sharma",
            "user_phone": "+91 98765 43210",
            "destination_id": "kalimpong",
            "latitude": 27.0667,
            "longitude": 88.4667,
            "nature_of_emergency": "Medical emergency",
            "idempotency_key": key
        }
        # First trigger
        res1 = client.post("/api/safety/sos", json=payload)
        assert res1.status_code == 200
        inc1_id = res1.json()["incident"]["incident_id"]

        # Second trigger with identical idempotency key
        res2 = client.post("/api/safety/sos", json=payload)
        assert res2.status_code == 200
        inc2 = res2.json()["incident"]
        assert inc2["incident_id"] == inc1_id
        assert inc2["repeat_count"] == 2

        # Check audit trail has DUPLICATE_SUPPRESSED
        actions = [a["action"] for a in inc2["audit_trail"]]
        assert "DUPLICATE_SUPPRESSED" in actions

    def test_rapid_tap_debounce_protects_against_panic_taps(self):
        """5 rapid taps within seconds create only 1 logical incident with repeat_count=5."""
        payload = {
            "user_name": "Panic User",
            "user_phone": "+91 99999 88888",
            "destination_id": "darjeeling",
            "nature_of_emergency": "Multiple panic clicks"
        }

        created_ids = []
        for _ in range(5):
            res = client.post("/api/safety/sos", json=payload)
            assert res.status_code == 200
            created_ids.append(res.json()["incident"]["incident_id"])

        # All 5 calls should resolve to the same unique incident_id
        assert len(set(created_ids)) == 1
        active_incidents = safety_incident_repository.list_active_incidents()
        assert len(active_incidents) == 1
        assert active_incidents[0].repeat_count == 5


class TestSosStateMachineAndTransitions:
    def test_full_successful_emergency_lifecycle(self):
        """CREATED -> DELIVERED -> ACKNOWLEDGED -> RESPONDING -> RESOLVED."""
        # 1. Trigger SOS
        res = client.post("/api/safety/sos", json={
            "user_name": "Deepak Rai",
            "user_phone": "+91 98111 00000",
            "destination_id": "kalimpong",
            "severity": "HIGH",
            "incident_type": "MEDICAL",
            "notes": "Ankle fracture on Deolo Hill descent"
        })
        inc_id = res.json()["incident"]["incident_id"]
        assert res.json()["incident"]["status"] == "DELIVERED"

        # 2. Operator Acknowledges
        ack_res = client.post(f"/api/admin/safety/incidents/{inc_id}/acknowledge", json={
            "operator_id": "op_kalimpong_desk",
            "notes": "Verified with traveler. Dispatched nearest Mitra unit."
        })
        assert ack_res.status_code == 200
        assert ack_res.json()["status"] == "ACKNOWLEDGED"
        assert ack_res.json()["assigned_operator"] == "op_kalimpong_desk"
        assert ack_res.json()["acknowledgement_latency_seconds"] is not None

        # 3. Operator Responds
        resp_res = client.post(f"/api/admin/safety/incidents/{inc_id}/respond", json={
            "operator_id": "op_kalimpong_desk",
            "notes": "Mitra Unit 4 arrived at location."
        })
        assert resp_res.status_code == 200
        assert resp_res.json()["status"] == "RESPONDING"

        # 4. Operator Resolves
        res_res = client.post(f"/api/admin/safety/incidents/{inc_id}/resolve", json={
            "operator_id": "op_kalimpong_desk",
            "notes": "Traveler transferred to Kalimpong District Hospital. Safe."
        })
        assert res_res.status_code == 200
        assert res_res.json()["status"] == "RESOLVED"
        assert res_res.json()["resolved_at"] is not None

        # 5. Check Audit Trail Integrity
        detail = client.get(f"/api/admin/safety/incidents/{inc_id}").json()
        actions = [a["action"] for a in detail["audit_trail"]]
        assert actions == ["CREATED", "ACKNOWLEDGED", "RESPONDING", "RESOLVED"]

    def test_invalid_state_transition_rejected(self):
        """DELIVERED incident cannot directly jump to RESOLVED without acknowledgement."""
        res = client.post("/api/safety/sos", json={
            "user_name": "Test Traveler",
            "user_phone": "+91 98222 33333",
            "nature_of_emergency": "Testing invalid jump"
        })
        inc_id = res.json()["incident"]["incident_id"]

        # Attempt illegal transition DELIVERED -> RESOLVED
        bad_res = client.post(f"/api/admin/safety/incidents/{inc_id}/resolve", json={
            "operator_id": "bad_actor",
            "notes": "Skipping ack and respond"
        })
        assert bad_res.status_code == 400
        assert "Cannot resolve incident from state DELIVERED" in bad_res.json()["detail"]

    def test_sos_accidental_cancellation(self):
        """Tourist cancels accidental tap. Incident is CANCELLED and never deleted."""
        res = client.post("/api/safety/sos", json={
            "user_name": "Accidental User",
            "user_phone": "+91 98333 44444",
            "nature_of_emergency": "Accidental tap while pocketed"
        })
        inc_id = res.json()["incident"]["incident_id"]

        # Cancel SOS
        cancel_res = client.post(f"/api/safety/sos/{inc_id}/cancel", json={
            "reason": "Was pocket dialed, no emergency",
            "cancelled_by": "TOURIST"
        })
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "CANCELLED"
        assert cancel_res.json()["cancellation_reason"] == "Was pocket dialed, no emergency"

        # Verify it still exists in admin listing
        all_incidents = client.get(f"/api/admin/safety/incidents?status=CANCELLED").json()
        assert any(i["incident_id"] == inc_id for i in all_incidents)


class TestEscalationAndSla:
    def test_manual_operator_escalation(self):
        res = client.post("/api/safety/sos", json={
            "user_name": "Severe Case",
            "user_phone": "+91 98444 55555",
            "severity": "CRITICAL",
            "nature_of_emergency": "Landslide blocking vehicle"
        })
        inc_id = res.json()["incident"]["incident_id"]

        # Escalate
        esc_res = client.post(f"/api/admin/safety/incidents/{inc_id}/escalate", json={
            "operator_id": "op_senior",
            "escalation_reason": "District Disaster Management support requested"
        })
        assert esc_res.status_code == 200
        assert esc_res.json()["status"] == "ESCALATED"
        assert esc_res.json()["escalation_level"] == 1
        assert "District Disaster" in esc_res.json()["escalation_reason"]

    def test_automated_sla_timeout_escalation(self):
        """Unacknowledged critical alert past timeout triggers automatic escalation."""
        # Create a critical incident with simulated delivered timestamp 60 seconds ago
        req = SosTriggerRequest(
            user_name="Timeout Case",
            user_phone="+91 98555 66666",
            severity=IncidentSeverity.CRITICAL,
            incident_type=IncidentType.ACCIDENT,
            nature_of_emergency="Critical mountain injury"
        )
        full_res = safety_operations_service.trigger_sos(req)
        inc = safety_incident_repository.get_incident(full_res.alert_id)
        # Backdate delivered_at
        inc.delivered_at = (datetime.utcnow() - timedelta(seconds=60)).isoformat()

        # Run timeout sweep
        escalated = safety_operations_service.check_escalation_timeouts()
        assert len(escalated) >= 1
        assert any(i.incident_id == inc.incident_id for i in escalated)

        # Confirm incident is now ESCALATED
        updated = safety_incident_repository.get_incident(inc.incident_id)
        assert updated.status == IncidentStatus.ESCALATED
        assert updated.escalation_level == 1


class TestOfflineQueueAndContacts:
    def test_offline_queued_sos_initial_state(self):
        """Offline-first client sets offline_queued=True -> status is DELIVERY_PENDING."""
        res = client.post("/api/safety/sos", json={
            "user_name": "Offline Hiker",
            "user_phone": "+91 98666 77777",
            "offline_queued": True,
            "nature_of_emergency": "Cached while off-grid in Neora Valley"
        })
        assert res.status_code == 200
        inc = res.json()["incident"]
        assert inc["status"] == "DELIVERY_PENDING"
        assert inc["delivered_at"] is None

    def test_official_contacts_directory(self):
        res = client.get("/api/safety/contacts")
        assert res.status_code == 200
        contacts = res.json()
        assert len(contacts) >= 4
        numbers = [c["contact_number"] for c in contacts]
        assert "112" in numbers
        assert "1363" in numbers
        for c in contacts:
            assert "OFFICIAL INFORMATION" in c["verification_label"]


class TestPrivacyAndRetention:
    def test_retention_scrubbing_redacts_coordinates_for_old_resolved_incidents(self):
        """Sensitive GPS coordinates scrubbed for resolved incidents older than threshold."""
        res = client.post("/api/safety/sos", json={
            "user_name": "Privacy Tourist",
            "user_phone": "+91 98777 88888",
            "latitude": 27.0667,
            "longitude": 88.4667,
            "nature_of_emergency": "Resolved yesterday"
        })
        inc_id = res.json()["incident"]["incident_id"]

        # Acknowledge and resolve
        client.post(f"/api/admin/safety/incidents/{inc_id}/acknowledge")
        client.post(f"/api/admin/safety/incidents/{inc_id}/resolve")

        # Backdate resolved_at to 48 hours ago
        inc = safety_incident_repository.get_incident(inc_id)
        inc.resolved_at = (datetime.utcnow() - timedelta(hours=48)).isoformat()

        # Run retention scrub for > 24 hours
        scrub_res = client.post("/api/admin/safety/retention/scrub?hours_threshold=24")
        assert scrub_res.status_code == 200
        assert scrub_res.json()["scrubbed_incidents"] >= 1

        # Check that coordinates are redacted but incident history remains
        scrubbed_inc = safety_incident_repository.get_incident(inc_id)
        assert scrubbed_inc.location.latitude is None
        assert scrubbed_inc.location.longitude is None
        assert scrubbed_inc.location.label == "REDACTED_PER_PRIVACY_RETENTION_POLICY"
        assert scrubbed_inc.status == IncidentStatus.RESOLVED


class TestDemandSegregationAndBackwardCompatibility:
    def test_sos_does_not_generate_tourism_demand_signals(self):
        """Mandatory: Emergency incidents must remain strictly segregated from tourism demand."""
        from app.services.demand_aggregation_service import demand_aggregation_service

        prior_count = len(demand_aggregation_service.get_raw_events())

        client.post("/api/safety/sos", json={
            "user_name": "Demand Isolation User",
            "user_phone": "+91 98888 99999",
            "destination_id": "darjeeling",
            "nature_of_emergency": "Distress test"
        })

        post_count = len(demand_aggregation_service.get_raw_events())
        # Emergency SOS must NOT append to tourism demand event history!
        assert post_count == prior_count


    def test_legacy_test_safety_sos_payload_continues_to_pass(self):
        """Verifies exact compatibility with the original test_api_endpoints.py test."""
        sos_payload = {
            "user_name": "Aarav Sharma",
            "user_phone": "+91 98765 43210",
            "destination_id": "kalimpong",
            "latitude": 27.0667,
            "longitude": 88.4667,
            "nature_of_emergency": "Medical / Sprain on Mountain Trail"
        }
        res = client.post("/api/safety/sos", json=sos_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ACTIVE_EMERGENCY_BROADCAST"
        assert len(data["nearest_responders"]) > 0
        assert "alert_id" in data
        assert "instructions_for_traveler" in data
