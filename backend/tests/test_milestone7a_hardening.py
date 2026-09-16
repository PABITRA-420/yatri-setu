"""
Milestone 7A Hardening Tests:
- Search Event & destination_id=None bug fix and deduplication
- Demand API endpoints (/demand/{id}, /demand/circuit, /admin/demand)
- 3-tier Provenance (SYNTHETIC, MIXED, REAL)
- Alternative Recommendation vs Acceptance Decoupling
- Single Homestay Repository & destination filtering
- Homestay Verification lifecycle & Panchayat visibility
- Booking resolution without silent fallback (404 on invalid)
- Trip Start idempotency and telemetry
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.services.demand_aggregation_service import demand_aggregation_service
from app.services.homestay_repository import homestay_repository
from app.models.demand import (
    DemandEventType,
    SearchEvent,
    DestinationSelectionEvent,
    AlternativeAcceptanceEvent,
    BookingEvent,
    AvailabilityEvent,
    TripStartEvent,
)

client = TestClient(app)


# =====================================================================
# 1. Search Event & None Destination Bug Fix
# =====================================================================

def test_search_with_valid_query_records_search_event():
    """Verify search records SearchEvent with destination_id=None and correct query."""
    initial_events = len(demand_aggregation_service.get_raw_events())

    res = client.get("/api/destinations?query=himalayan%20views")
    assert res.status_code == 200

    events = demand_aggregation_service.get_raw_events()
    assert len(events) == initial_events + 1

    latest = events[-1]
    assert latest.event_type == DemandEventType.SEARCH
    assert latest.destination_id is None
    assert latest.metadata.get("query") == "himalayan views"
    assert latest.is_synthetic is False


def test_search_with_empty_or_whitespace_records_no_event():
    """Verify empty or whitespace search queries do not record search events."""
    initial_events = len(demand_aggregation_service.get_raw_events())

    res1 = client.get("/api/destinations?query=")
    assert res1.status_code == 200

    res2 = client.get("/api/destinations?query=   ")
    assert res2.status_code == 200

    events = demand_aggregation_service.get_raw_events()
    assert len(events) == initial_events


def test_search_rapid_duplicate_deduplication_5s():
    """Verify rapid repeated queries (<5s) are deduplicated."""
    unique_query = f"tea_garden_special_{datetime.utcnow().timestamp()}"

    res1 = client.get(f"/api/destinations?query={unique_query}")
    assert res1.status_code == 200

    count_after_first = len(demand_aggregation_service.get_raw_events())

    # Second immediate query
    res2 = client.get(f"/api/destinations?query={unique_query}")
    assert res2.status_code == 200

    count_after_second = len(demand_aggregation_service.get_raw_events())
    assert count_after_second == count_after_first  # Deduplicated!


# =====================================================================
# 2. Demand Event Types Coverage
# =====================================================================

def test_all_demand_event_types_record_properly():
    """Verify all required event models record without exceptions."""
    # 1. Destination selection
    sel = DestinationSelectionEvent(
        destination_id="kalimpong",
        source="web",
        session_id="test-sess-01",
        user_id="u-01",
        view_source="search_results"
    )
    res_sel = demand_aggregation_service.record_event(sel)
    assert res_sel.get("status") == "recorded"

    # 2. Availability event
    avail = AvailabilityEvent(
        destination_id="lava",
        homestay_id="hs-lava-01",
        date="2026-10-01",
        available_capacity=4,
        is_available=True,
        source="host_update"
    )
    res_avail = demand_aggregation_service.record_event(avail)
    assert res_avail.get("status") == "recorded"

    # 3. Booking event
    bk = BookingEvent(
        destination_id="kalimpong",
        homestay_id="hs-kalimpong-01",
        booking_id="bk-test-01",
        num_guests=2,
        num_nights=3,
        source="web"
    )
    res_bk = demand_aggregation_service.record_event(bk)
    assert res_bk.get("status") == "recorded"


# =====================================================================
# 3. Demand API Endpoints & Privacy
# =====================================================================

def test_demand_api_destination_endpoint():
    """GET /api/demand/{id} returns demand metrics without raw events or PII."""
    res = client.get("/api/demand/kalimpong")
    assert res.status_code == 200
    data = res.json()

    assert data["destination_id"] == "kalimpong"
    assert "search_count_7d" in data
    assert "booking_count_7d" in data
    assert "availability_pressure" in data
    assert "provenance_label" in data
    assert "provider_mode" in data
    # Ensure no PII or raw user IDs are exposed
    assert "user_id" not in data
    assert "raw_events" not in data


def test_demand_api_circuit_endpoint():
    """GET /api/demand/circuit returns aggregated circuit demand."""
    res = client.get("/api/demand/circuit")
    assert res.status_code == 200
    data = res.json()

    assert data["circuit_id"] in ["darjeeling_kalimpong_circuit", "darjeeling-kalimpong-circuit"]
    assert "summary" in data
    assert "destinations" in data
    assert "total_searches_7d" in data["summary"]
    assert "total_bookings_7d" in data["summary"]
    assert "provenance_label" in data["summary"]
    # Check that destinations are present
    assert "kalimpong" in data["destinations"]


def test_demand_api_admin_endpoint():
    """GET /api/admin/demand returns admin overview with provenance audit."""
    res = client.get("/api/admin/demand")
    assert res.status_code == 200
    data = res.json()

    assert "total_events_recorded" in data
    assert "event_breakdown" in data
    assert "conversion_funnel" in data
    assert "provenance_audit" in data
    audit = data["provenance_audit"]
    assert "provenance_label" in audit
    assert "real_events_count" in audit
    assert "synthetic_events_count" in audit
    assert audit["provenance_label"] in [
        "SYNTHETIC DEMO DATA",
        "MIXED — YATRI SETU NETWORK + SYNTHETIC DEMO",
        "REAL — YATRI SETU NETWORK"
    ]


# =====================================================================
# 4. Strict Provenance Progression
# =====================================================================

def test_provenance_reflects_network_activity():
    """Verify provenance reflects synthetic vs real network events."""
    overview = demand_aggregation_service.get_admin_overview()
    audit = overview.provenance_audit if hasattr(overview, "provenance_audit") else overview["provenance_audit"]

    # Since we recorded real events above, provenance should be MIXED
    real_count = audit.get("real_events_count") if isinstance(audit, dict) else audit.real_events_count
    synth_count = audit.get("synthetic_events_count") if isinstance(audit, dict) else audit.synthetic_events_count
    label = audit.get("provenance_label") if isinstance(audit, dict) else audit.provenance_label
    mode = audit.get("mode") if isinstance(audit, dict) else audit.mode

    assert real_count > 0
    assert synth_count > 0
    assert label == "MIXED — YATRI SETU NETWORK + SYNTHETIC DEMO"
    assert mode == "MIXED"


# =====================================================================
# 5. Alternative Recommendation vs Acceptance Decoupling
# =====================================================================

def test_flow_decision_recommendation_does_not_record_acceptance():
    """Calling flow-decision for alternatives does NOT emit ALTERNATIVE_ACCEPTANCE."""
    overview_before = demand_aggregation_service.get_admin_overview()
    funnel_before = overview_before.conversion_funnel if hasattr(overview_before, "conversion_funnel") else overview_before["conversion_funnel"]
    accept_count_before = funnel_before.get("alternative_acceptances") if isinstance(funnel_before, dict) else funnel_before.alternative_acceptances

    # Request alternatives for Darjeeling
    res = client.post(
        "/api/destinations/darjeeling/decision",
        json={"budget": "standard", "interests": ["nature", "culture"]}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data.get("alternative_destinations", [])) > 0

    overview_after = demand_aggregation_service.get_admin_overview()
    funnel_after = overview_after.conversion_funnel if hasattr(overview_after, "conversion_funnel") else overview_after["conversion_funnel"]
    accept_count_after = funnel_after.get("alternative_acceptances") if isinstance(funnel_after, dict) else funnel_after.alternative_acceptances

    # The count must remain unchanged!
    assert accept_count_after == accept_count_before


def test_explicit_alternative_acceptance_records_event():
    """Calling accept-alternative explicitly emits ALTERNATIVE_ACCEPTANCE with deduplication."""
    overview_before = demand_aggregation_service.get_admin_overview()
    funnel_before = overview_before.conversion_funnel if hasattr(overview_before, "conversion_funnel") else overview_before["conversion_funnel"]
    accept_count_before = funnel_before.get("alternative_acceptances") if isinstance(funnel_before, dict) else funnel_before.alternative_acceptances

    res = client.post(
        "/api/destinations/darjeeling/accept-alternative",
        json={
            "alternative_destination_id": "lava",
            "redirect_reason": "crowd_avoidance",
            "original_crowd_score": 88,
            "session_id": "sess-test-alt-01"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "recorded"
    assert data["original_destination_id"] == "darjeeling"
    assert data["alternative_destination_id"] == "lava"

    overview_after = demand_aggregation_service.get_admin_overview()
    funnel_after = overview_after.conversion_funnel if hasattr(overview_after, "conversion_funnel") else overview_after["conversion_funnel"]
    accept_count_after = funnel_after.get("alternative_acceptances") if isinstance(funnel_after, dict) else funnel_after.alternative_acceptances
    assert accept_count_after == accept_count_before + 1

    # Immediate duplicate request with same session and destination within 5s
    res_dup = client.post(
        "/api/destinations/darjeeling/accept-alternative",
        json={
            "alternative_destination_id": "lava",
            "redirect_reason": "crowd_avoidance",
            "original_crowd_score": 88,
            "session_id": "sess-test-alt-01"
        }
    )
    assert res_dup.status_code == 200
    assert res_dup.json()["status"] == "duplicate"


# =====================================================================
# 6. Single Homestay Repository & Destination Filtering
# =====================================================================

def test_homestays_filter_by_destination():
    """GET /api/homestays respects destination_id and returns empty for Darjeeling."""
    # 1. Kalimpong -> returns Kalimpong homestays
    res_k = client.get("/api/homestays?destination_id=kalimpong")
    assert res_k.status_code == 200
    k_homes = res_k.json()
    assert len(k_homes) >= 2
    for h in k_homes:
        assert h["destination_id"] == "kalimpong"

    # 2. Darjeeling -> returns empty list (no homestays in pilot hub)
    res_d = client.get("/api/homestays?destination_id=darjeeling")
    assert res_d.status_code == 200
    assert res_d.json() == []

    # 3. Mirik -> returns empty list
    res_m = client.get("/api/homestays?destination_id=mirik")
    assert res_m.status_code == 200
    assert res_m.json() == []

    # 4. Missing destination_id -> returns all verified homestays across circuit
    res_all = client.get("/api/homestays")
    assert res_all.status_code == 200
    all_homes = res_all.json()
    assert len(all_homes) >= 4
    dest_ids = set(h["destination_id"] for h in all_homes)
    assert "kalimpong" in dest_ids
    assert "lava" in dest_ids or "rishop" in dest_ids


# =====================================================================
# 7. Homestay Verification Lifecycle & Panchayat Visibility
# =====================================================================

def test_homestay_verification_lifecycle_panchayat():
    """Unapproved homestay is hidden; once verified by Panchayat, it becomes visible."""
    test_id = "hs-test-pending-01"

    # Register onboarding in SUBMITTED state
    homestay_repository.register_onboarding(
        homestay_id=test_id,
        name="Test Hill View Retreat",
        destination_id="lava",
        village="Lava",
        panchayat_name="Lava Gram Panchayat",
        rooms_count=2,
        price_inr=1800,
        host_id="host-test-99",
        host_name="Tenzing Test",
        status="SUBMITTED"
    )

    # Tourist search should NOT show SUBMITTED homestay
    res_before = client.get("/api/homestays?destination_id=lava")
    assert res_before.status_code == 200
    lava_ids_before = [h["id"] for h in res_before.json()]
    assert test_id not in lava_ids_before

    # Panchayat verifies homestay
    updated = homestay_repository.update_verification_status(test_id, "VERIFIED")
    assert updated is True

    # Tourist search SHOULD now show VERIFIED homestay
    res_after = client.get("/api/homestays?destination_id=lava")
    assert res_after.status_code == 200
    lava_ids_after = [h["id"] for h in res_after.json()]
    assert test_id in lava_ids_after


# =====================================================================
# 8. Booking Consistency & No Silent Fallback (404 on Invalid)
# =====================================================================

def test_booking_valid_homestay_resolves_correct_destination():
    """Booking existing homestay resolves authoritative destination_id."""
    res = client.post(
        "/api/bookings",
        json={
            "homestay_id": "hs-kalimpong-01",
            "traveler_name": "Anita Roy",
            "traveler_phone": "+91 9876543210",
            "traveler_email": "anita@example.com",
            "emergency_contact": "+91 9876543211",
            "check_in_date": "2026-11-01",
            "check_out_date": "2026-11-04",
            "number_of_guests": 2
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["homestay"]["id"] == "hs-kalimpong-01"
    assert data["homestay"]["destination_id"] == "kalimpong"


def test_booking_invalid_homestay_returns_404():
    """Booking nonexistent homestay returns 404 and does NOT fallback silently."""
    res = client.post(
        "/api/bookings",
        json={
            "homestay_id": "hs-nonexistent-invalid-999",
            "traveler_name": "Ghost Traveler",
            "traveler_phone": "+91 9876543210",
            "traveler_email": "ghost@example.com",
            "emergency_contact": "+91 9876543211",
            "check_in_date": "2026-11-01",
            "check_out_date": "2026-11-04",
            "number_of_guests": 2
        }
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# =====================================================================
# 9. Trip Start Idempotency
# =====================================================================

def test_trip_start_idempotency():
    """POST /api/trips/{trip_id}/start is idempotent and records TripStartEvent only once."""
    events_before = len(demand_aggregation_service.get_raw_events())
    trip_id = f"trip-test-{int(datetime.utcnow().timestamp())}"

    # First start call
    res1 = client.post(f"/api/trips/{trip_id}/start")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["trip_id"] == trip_id
    assert data1["status"] in ["IN_PROGRESS", "STARTED", "Journey In Progress"]

    events_mid = len(demand_aggregation_service.get_raw_events())
    assert events_mid == events_before + 1

    # Repeated start call with same trip_id
    res2 = client.post(f"/api/trips/{trip_id}/start")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["trip_id"] == trip_id
    assert data2["status"] == data1["status"]

    # Event count must NOT increment on second call
    events_after = len(demand_aggregation_service.get_raw_events())
    assert events_after == events_mid
