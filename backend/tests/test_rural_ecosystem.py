import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.host_service import host_service
from app.services.panchayat_service import panchayat_service
from app.services.flow_impact_service import flow_impact_service
from app.models.host import VoiceDraftRequest

client = TestClient(app)

def test_host_earnings_deterministic_calculation():
    """Validates deterministic breakdown: Gross 100%, Platform 5%, Community 5%, Host 90%."""
    gross = 10000
    calc = host_service.calculate_earnings(gross)
    assert calc["booking_value"] == 10000
    assert calc["platform_fee"] == 500
    assert calc["community_fund_contribution"] == 500
    assert calc["host_earning"] == 9000
    assert calc["platform_fee"] + calc["community_fund_contribution"] + calc["host_earning"] == gross

def test_host_onboarding_and_verification_state():
    """Tests host registration and ensures initial status is strictly SUBMITTED."""
    payload = {
        "name": "Karma Lhamo",
        "phone": "+91 98321 44556",
        "email": "karma.lhamo@testrural.org",
        "village": "Lava Neora Forest Fringe",
        "panchayat_name": "Lava Forest Range Panchayat",
        "destination_id": "lava",
        "languages": ["English", "Nepali", "Lepcha"],
        "bio": "Organic cardamom farmer and traditional cook.",
        "homestay_title": "Lava Mist Forest Cottage",
        "tagline": "Wake up to mountain birdcalls at the forest edge",
        "address": "Algarah Road, Lava, Kalimpong - 734319",
        "room_type": "Pine Wood Attic",
        "rooms_count": 2,
        "max_guests": 4,
        "price_per_night_inr": 1800,
        "amenities": ["Organic Farm Dining", "Wood Fireplace"],
        "sustainability_attributes": ["Zero Single-Use Plastic", "Spring Water Source"],
        "special_activity": "Cardamom curing workshop"
    }
    response = client.post("/api/hosts/onboard", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "host" in data
    assert "listing" in data
    assert data["host"]["name"] == "Karma Lhamo"
    assert data["host"]["verification"]["status"] == "SUBMITTED"
    assert data["listing"]["verification_status"] == "SUBMITTED"
    assert data["listing"]["is_published"] is False # Not published to tourists until verified

def test_voice_listing_assistant_guardrails():
    """
    Validates prototype voice assistant:
    Converts speech transcript to draft listing.
    STRICT GUARDRAIL: AI must NOT invent prices, verification status, or identity.
    """
    req = VoiceDraftRequest(
        spoken_text="We have a two-room homestay near Lava. We provide homemade food and forest walks."
    )
    draft = host_service.parse_voice_listing(req)
    assert draft.detected_destination_id == "lava"
    assert draft.suggested_rooms_count == 2
    assert "Authentic Homemade Village Meals" in draft.detected_amenities
    assert "Guided Forest & Nature Trail Walks" in draft.detected_amenities
    # Safety guardrails
    assert draft.price_requires_host_input is True
    assert draft.verification_status == "SUBMITTED"
    assert "strictly NOT set pricing" in draft.warning_guardrail

def test_panchayat_verification_approval_workflow():
    """Tests Panchayat reviewing, approving, and publishing a homestay with audit notes."""
    # First onboard a new listing
    res_onboard = client.post("/api/hosts/onboard", json={
        "name": "Chhiring Sherpa",
        "phone": "+91 98322 11223",
        "email": "chhiring@test.com",
        "village": "Rishop Ridge",
        "panchayat_name": "Rishop Ridge Panchayat",
        "destination_id": "rishop",
        "languages": ["Nepali", "English"],
        "bio": "Mountaineer and local guide",
        "homestay_title": "Rishop Kanchenjunga Viewpoint Homestay",
        "tagline": "Unobstructed sunrise vistas",
        "address": "Top Ridge, Rishop",
        "room_type": "Wooden Cottage",
        "rooms_count": 3,
        "max_guests": 6,
        "price_per_night_inr": 2200,
        "amenities": ["Hot Water", "Heated Blankets"],
        "sustainability_attributes": ["Composted Organic Waste"],
        "special_activity": "Tiffin Dara sunrise hike"
    })
    listing_id = res_onboard.json()["listing"]["id"]

    # Panchayat reviews and approves
    decision_payload = {
        "action": "APPROVE",
        "reason": "Physical premises inspected. Fire safety bucket, organic composting, and spring filter verified.",
        "reviewer_name": "Panchayat Officer Pemba Norbu"
    }
    dec_res = client.post(f"/api/panchayat/verifications/{listing_id}/decision", json=decision_payload)
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    assert dec_data["new_status"] == "VERIFIED"
    assert dec_data["reviewer_name"] == "Panchayat Officer Pemba Norbu"

    # Verify listing is now VERIFIED and published
    updated_listing = host_service.get_listing_by_id(listing_id)
    assert updated_listing.verification_status == "VERIFIED"
    assert updated_listing.is_published is True

def test_panchayat_verification_rejection_workflow():
    """Tests Panchayat rejecting a homestay with civic audit remarks."""
    res_onboard = client.post("/api/hosts/onboard", json={
        "name": "Test Unsafe Host",
        "phone": "+91 98000 00001",
        "email": "unsafe@test.com",
        "village": "Lolegaon Forest Edge",
        "panchayat_name": "Lolegaon Heritage Panchayat",
        "destination_id": "lolegaon",
        "languages": ["Nepali"],
        "bio": "New host",
        "homestay_title": "Incomplete Homestay",
        "tagline": "Under construction",
        "address": "Kaffer Road",
        "room_type": "Room",
        "rooms_count": 1,
        "max_guests": 2,
        "price_per_night_inr": 1000,
        "amenities": ["None"],
        "sustainability_attributes": [],
        "special_activity": "None"
    })
    listing_id = res_onboard.json()["listing"]["id"]

    dec_payload = {
        "action": "REJECT",
        "reason": "Incomplete sanitation plumbing and lack of emergency first aid kit.",
        "reviewer_name": "Panchayat Nodal Officer Pemba Norbu"
    }
    dec_res = client.post(f"/api/panchayat/verifications/{listing_id}/decision", json=dec_payload)
    assert dec_res.status_code == 200
    assert dec_res.json()["new_status"] == "REJECTED"

    updated_listing = host_service.get_listing_by_id(listing_id)
    assert updated_listing.verification_status == "REJECTED"
    assert updated_listing.is_published is False

def test_local_experiences_seed_and_creation():
    """Tests GET and POST /api/experiences across all 6 destinations."""
    # List verified experiences
    res = client.get("/api/experiences")
    assert res.status_code == 200
    exps = res.json()
    assert len(exps) >= 6
    dest_ids = {e["destination_id"] for e in exps}
    assert "darjeeling" in dest_ids
    assert "kalimpong" in dest_ids
    assert "lava" in dest_ids
    assert "rishop" in dest_ids

    # Create new experience
    new_exp_payload = {
        "title": "Neora Ridge Wild Orchid & Rhododendron Walk",
        "description": "Guided forest walk to spot endemic wild orchids.",
        "host_id": "host-kalim-01",
        "destination_id": "lava",
        "duration_hours": 2.5,
        "price_inr": 850,
        "capacity": 6,
        "languages": ["English", "Nepali"],
        "category": "Forest & Wildlife",
        "highlights": ["Wild orchid spotting"]
    }
    create_res = client.post("/api/experiences", json=new_exp_payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["title"] == "Neora Ridge Wild Orchid & Rhododendron Walk"
    assert created["verification_status"] == "UNDER_REVIEW"

def test_tourism_flow_impact_calculation():
    """Tests GET /api/impact/destination/{id} for Darjeeling vs rural alternative."""
    # High pressure destination (Darjeeling)
    res_darj = client.get("/api/impact/destination/darjeeling")
    assert res_darj.status_code == 200
    darj_data = res_darj.json()
    assert darj_data["is_congested_hub"] is True
    assert darj_data["redirected_tourists_count"] > 300
    assert darj_data["estimated_local_revenue_inr"] > 1000000
    assert darj_data["crowd_pressure_reduction_percent"] > 25.0
    assert len(darj_data["beneficiary_villages"]) >= 3

    # Rural destination (Kalimpong)
    res_kalim = client.get("/api/impact/destination/kalimpong")
    assert res_kalim.status_code == 200
    kalim_data = res_kalim.json()
    assert kalim_data["is_congested_hub"] is False
    assert kalim_data["redirected_tourists_count"] > 100
    assert kalim_data["estimated_local_revenue_inr"] > 500000
    assert kalim_data["community_fund_generated_inr"] > 20000

def test_booking_integration_with_rural_earnings():
    """Tests that simulated booking computes host earnings, platform fee, and prototype payment status."""
    booking_req = {
        "homestay_id": "hs-kalim-01",
        "traveler_name": "Rohan Deshpande",
        "traveler_phone": "+91 98200 55443",
        "traveler_email": "rohan.d@gmail.com",
        "emergency_contact": "+91 98200 11223",
        "check_in_date": "2026-10-10",
        "check_out_date": "2026-10-13",
        "number_of_guests": 2
    }
    res = client.post("/api/bookings", json=booking_req)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CONFIRMED"
    assert data["payment_status"] == "PROTOTYPE_ESCROW_CONFIRMED"
    assert data["platform_fee_inr"] > 0
    assert data["host_earning_inr"] > 0
    assert data["community_fund_contribution_inr"] > 0
    assert data["homestay"]["panchayat_verified"] is True
    assert data["homestay"]["sustainable_stay_badge"] is True
