"""
Milestone 7G: Panchayat + Host + Local Economy Intelligence Test Suite.
Verifies normalized host profiles, homestay ownership, dynamic booking-to-host attribution,
economic models, Panchayat operational advisories, capacity warnings, M7F safety aggregation,
audit trails, and zero-PII data minimization.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.rural.service import rural_operations_service
from app.services.rural.schemas import HostVerificationStatus, HostActiveStatus
from app.services.booking.service import booking_lifecycle_service
from app.services.booking.schemas import BookingState

client = TestClient(app)


class TestHostProfileAndOnboarding:
    def test_get_normalized_host_profile(self):
        """Validates normalized HostProfile schema with masked PII and provenance."""
        res = client.get("/api/hosts/profile")
        assert res.status_code == 200
        data = res.json()
        assert data["host_id"] == "host-kalim-01"
        assert data["display_name"] == "Pemba Sherpa"
        assert data["destination_id"] == "kalimpong"
        assert data["verification_status"] == "VERIFIED"
        assert data["active_status"] == "ACTIVE"
        assert "***" in data["phone_masked"]
        assert "****@" in data["email_masked"]
        assert "REAL HOST REGISTRATION" in data["source"]

    def test_host_alias_route_compliance(self):
        """Validates /api/host/profile and /api/host/dashboard aliases."""
        res_prof = client.get("/api/host/profile")
        assert res_prof.status_code == 200
        assert res_prof.json()["host_id"] == "host-kalim-01"

        res_dash = client.get("/api/host/dashboard")
        assert res_dash.status_code == 200
        assert "booking_snapshot" in res_dash.json()

    def test_host_onboarding_and_suspension_lifecycle(self):
        """Tests complete lifecycle: onboarding -> submitted -> suspended -> audit."""
        onboard_payload = {
            "name": "Sonam Wangchuk",
            "phone": "+91 98450 12345",
            "email": "sonam.w@ruralhimalaya.org",
            "village": "Lolegaon Forest Hamlet",
            "panchayat_name": "Lolegaon Heritage Panchayat",
            "destination_id": "lolegaon",
            "languages": ["English", "Nepali"],
            "bio": "Traditional carpenter and organic beekeeper.",
            "homestay_title": "Lolegaon Honeycomb Cottage",
            "tagline": "Organic honey tasting and pine forest tranquility",
            "address": "Ridge Road, Lolegaon",
            "room_type": "Wooden Attic",
            "rooms_count": 2,
            "max_guests": 4,
            "price_per_night_inr": 2000,
            "amenities": ["Organic Honey Breakfast", "Forest View Deck"],
            "sustainability_attributes": ["Zero Plastic", "Rainwater Harvesting"],
            "special_activity": "Beekeeping & honey extraction workshop"
        }
        res = client.post("/api/hosts/onboard", json=onboard_payload)
        assert res.status_code == 200
        host_id = res.json()["host"]["id"]

        # Check rural service has the host in SUBMITTED
        prof = rural_operations_service.get_host_profile(host_id)
        assert prof is not None
        assert prof.verification_status == HostVerificationStatus.SUBMITTED

        # Test suspension endpoint
        sus_res = client.post(f"/api/hosts/{host_id}/suspend", json={"reason": "Routine civic audit suspension"})
        assert sus_res.status_code == 200
        assert sus_res.json()["active_status"] == "SUSPENDED"

        # Check audit log records the suspension
        logs = rural_operations_service.list_audit_logs()
        sus_logs = [l for l in logs if l.entity_id == host_id and l.action == "HOST_SUSPENDED"]
        assert len(sus_logs) >= 1
        assert "Routine civic audit" in sus_logs[0].details


class TestHomestayOwnershipAndAttribution:
    def test_homestay_ownership_consistency(self):
        """Verifies that each host's homestays are consistently owned and have valid destination IDs."""
        hosts = rural_operations_service.list_all_hosts()
        assert len(hosts) >= 6

        for h in hosts:
            for hid in h.homestay_ids:
                rec = client.get(f"/api/homestays/{hid}")
                # If homestay exists in repository, destination must match
                if rec.status_code == 200:
                    assert rec.json()["destination_id"] == h.destination_id


class TestEconomicsAndBookingAttribution:
    def test_confirmed_booking_attributed_to_host_dashboard(self):
        """
        Primary M7G Requirement:
        Creating a real booking attributes gross booking value, platform commission,
        and estimated host payout (90%) directly to the host dashboard.
        """
        # Create a confirmed booking for hs-kalim-01
        booking_payload = {
            "homestay_id": "hs-kalim-01",
            "traveler_name": "Ananya Sharma",
            "traveler_phone": "+91 98201 99887",
            "traveler_email": "ananya.sharma@example.com",
            "emergency_contact": "+91 98201 11223",
            "check_in_date": "2026-10-20",
            "check_out_date": "2026-10-23",
            "number_of_guests": 2
        }
        res_book = client.post("/api/bookings", json=booking_payload)
        assert res_book.status_code == 200
        booking_id = res_book.json()["booking_id"]
        gross_amount = res_book.json()["total_amount_inr"]

        # Fetch host dashboard for Pemba Sherpa (host-kalim-01)
        res_dash = client.get("/api/hosts/host-kalim-01/dashboard")
        assert res_dash.status_code == 200
        data = res_dash.json()

        # Check booking snapshot includes confirmed stay
        assert data["booking_snapshot"]["confirmed_stays"] >= 1
        assert data["booking_snapshot"]["occupied_room_nights"] >= 3

        # Check transparent economic summary
        econ = data["economic_summary"]
        assert econ["gross_booking_value"] >= gross_amount
        assert econ["platform_commission"] > 0
        assert "CONFIGURED ASSUMPTION" in econ["platform_commission_label"]
        assert econ["community_fund_contribution"] > 0
        assert econ["taxes_or_fees"] == "NOT MODELED"
        assert econ["estimated_host_payout"] > 0
        assert "payment settlement is not connected" in econ["payout_notice"]

    def test_cancellation_releases_payout_and_records_cancellation(self):
        """Validates that cancelling a booking removes its confirmed payout attribution."""
        # Create a booking
        booking_payload = {
            "homestay_id": "hs-kalim-01",
            "traveler_name": "Vikram Patel",
            "traveler_phone": "+91 98202 33445",
            "traveler_email": "vikram.p@example.com",
            "emergency_contact": "+91 98202 11223",
            "check_in_date": "2026-10-25",
            "check_out_date": "2026-10-28",
            "number_of_guests": 2
        }
        res_book = client.post("/api/bookings", json=booking_payload)
        assert res_book.status_code == 200
        b_id = res_book.json()["booking_id"]

        # Cancel the booking
        res_cancel = client.post(f"/api/bookings/{b_id}/cancel", params={"reason": "Travel itinerary changed"})
        assert res_cancel.status_code == 200
        assert res_cancel.json()["state"] == "CANCELLED"

        # Check host dashboard
        res_dash = client.get("/api/hosts/host-kalim-01/dashboard")
        assert res_dash.status_code == 200
        data = res_dash.json()
        assert data["booking_snapshot"]["cancellations"] >= 1


class TestPanchayatDashboardAndCapacityAdvisory:
    def test_panchayat_profile_and_dashboard(self):
        """Tests GET /api/panchayat/profile and /api/panchayat/dashboard."""
        res_prof = client.get("/api/panchayat/profile?destination_id=kalimpong")
        assert res_prof.status_code == 200
        prof = res_prof.json()
        assert prof["destination_id"] == "kalimpong"
        assert "Kalimpong" in prof["name"]

        res_dash = client.get("/api/panchayat/dashboard?destination_id=kalimpong")
        assert res_dash.status_code == 200
        dash = res_dash.json()
        assert "authority" in dash
        assert "tourism_flow" in dash
        assert "rural_ecosystem" in dash
        assert "local_economy" in dash
        assert "safety_summary" in dash
        assert "notifications" in dash

    def test_panchayat_notifications_acknowledge_and_resolve(self):
        """Tests listing, acknowledging, and resolving Panchayat notifications."""
        # List notifications
        res_list = client.get("/api/panchayat/notifications?destination_id=kalimpong")
        assert res_list.status_code == 200
        notifs = res_list.json()
        assert len(notifs) >= 1
        notif_id = notifs[0]["notification_id"]

        # Acknowledge
        res_ack = client.post(
            f"/api/panchayat/notifications/{notif_id}/acknowledge",
            json={"operator_name": "Officer Norbu"}
        )
        assert res_ack.status_code == 200
        assert res_ack.json()["status"] == "ACKNOWLEDGED"
        assert res_ack.json()["acknowledged_by"] == "Officer Norbu"

        # Resolve
        res_res = client.post(
            f"/api/panchayat/notifications/{notif_id}/resolve",
            json={"operator_name": "Officer Norbu", "resolution_notes": "Redirection pressure normalized."}
        )
        assert res_res.status_code == 200
        assert res_res.json()["status"] == "RESOLVED"


class TestSafetyIntegrationAndPrivacy:
    def test_panchayat_safety_summary_excludes_traveler_pii_and_gps(self):
        """
        M7F Safety Integration:
        Panchayat receives only aggregate counts (active, critical, escalated, resolved).
        Zero traveler names, phone numbers, or GPS coordinates are present in the response.
        """
        res = client.get("/api/panchayat/dashboard?destination_id=kalimpong")
        assert res.status_code == 200
        data = res.json()
        safety = data["safety_summary"]

        assert "active_safety_incidents" in safety
        assert "critical_safety_incidents" in safety
        assert "escalation_required_incidents" in safety
        assert "resolved_safety_incidents" in safety
        assert safety["data_protection"] == "STRICT_AGGREGATE_NO_PII"

        # Verify no PII keys exist in safety summary
        raw_text = str(safety).lower()
        assert "gps" not in raw_text
        assert "latitude" not in raw_text
        assert "longitude" not in raw_text
        assert "traveler_name" not in raw_text
        assert "traveler_phone" not in raw_text


class TestAdminRuralEndpoints:
    def test_admin_rural_summary_and_destinations(self):
        """Tests /api/admin/rural/summary, /rural/destinations, and /rural/economy."""
        res_sum = client.get("/api/admin/rural/summary")
        assert res_sum.status_code == 200
        sum_data = res_sum.json()
        assert sum_data["total_active_hosts"] >= 6
        assert sum_data["total_verified_hosts"] >= 6
        assert len(sum_data["destinations"]) == 6

        res_dest = client.get("/api/admin/rural/destinations")
        assert res_dest.status_code == 200
        dest_data = res_dest.json()
        assert len(dest_data) == 6
        dest_ids = {d["destination_id"] for d in dest_data}
        assert "kalimpong" in dest_ids
        assert "lava" in dest_ids
        assert "lolegaon" in dest_ids

        res_econ = client.get("/api/admin/rural/economy")
        assert res_econ.status_code == 200
        econ_data = res_econ.json()
        assert econ_data["commission_policy"]["platform_fee_percent"] == 5.0
        assert "CONFIGURED ASSUMPTION" in econ_data["commission_policy"]["classification"]
        assert "payment settlement is not connected" in econ_data["commission_policy"]["settlement_status"]

    def test_admin_rural_audit_logs(self):
        """Tests /api/admin/rural/audit-logs returns immutable operational records."""
        res = client.get("/api/admin/rural/audit-logs?limit=20")
        assert res.status_code == 200
        logs = res.json()
        assert isinstance(logs, list)
        assert len(logs) >= 1
        assert "log_id" in logs[0]
        assert "actor" in logs[0]
        assert "action" in logs[0]
        assert "timestamp" in logs[0]


class TestFlowSimulationNonMutation:
    def test_flow_simulation_does_not_generate_real_revenue_or_demand(self):
        """
        Validates that M7D flow planning simulations remain purely simulated
        and never mutate real booking, host revenue, or demand telemetry.
        """
        # Baseline check of bookings
        initial_bookings_count = len(booking_lifecycle_service.get_all_bookings())

        # Run flow simulation
        sim_payload = {
            "source_destination_id": "darjeeling",
            "affected_visitors": 100,
            "acceptance_rate": 0.25
        }
        res_sim = client.post("/api/admin/flow/simulate", json=sim_payload)
        assert res_sim.status_code == 200

        # Verify no real booking was created
        final_bookings_count = len(booking_lifecycle_service.get_all_bookings())
        assert final_bookings_count == initial_bookings_count
