from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

def test_list_destinations():
    res = client.get("/api/destinations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 6
    names = [d["name"] for d in data]
    assert "Darjeeling" in names
    assert "Kalimpong" in names

def test_crowd_endpoint():
    res = client.get("/api/destinations/darjeeling/crowd")
    assert res.status_code == 200
    data = res.json()
    assert data["destination_id"] == "darjeeling"
    assert data["crowd_score"] >= 60
    assert data["crowd_level"] in ("HIGH", "VERY HIGH")
    assert len(data["why_crowded"]) > 0
    # Canonical V2 fields
    assert "pressure_score" in data
    assert "confidence" in data
    assert len(data["factors"]) == 8

def test_alternatives_endpoint():
    res = client.get("/api/destinations/darjeeling/alternatives")
    assert res.status_code == 200
    data = res.json()
    assert data["origin_destination_id"] == "darjeeling"
    assert len(data["alternatives"]) > 0
    top = data["alternatives"][0]
    assert top["id"] == "kalimpong"
    assert top["similarity_score"] == 87
    assert top["original_crowd_score"] >= 60
    assert top["crowd_reduction_percent"] >= 25
    assert len(top["matching_attributes"]) > 0

def test_date_alternatives_endpoint():
    res = client.get(
        "/api/destinations/darjeeling/date-alternatives?preferred_start_date=2026-12-25&preferred_end_date=2026-12-27"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["destination_id"] == "darjeeling"
    assert data["preferred_crowd_score"] >= 88
    assert len(data["date_alternatives"]) == 3
    assert data["date_alternatives"][0]["crowd_reduction_percent"] > 50

def test_date_alternatives_invalid_dates():
    res = client.get(
        "/api/destinations/darjeeling/date-alternatives?preferred_start_date=2026-12-27&preferred_end_date=2026-12-25"
    )
    assert res.status_code == 400

    res2 = client.get(
        "/api/destinations/nonexistent_place/date-alternatives?preferred_start_date=2026-12-25&preferred_end_date=2026-12-27"
    )
    assert res2.status_code == 404

def test_decision_endpoints():
    get_res = client.get("/api/destinations/darjeeling/decision?start_date=2026-12-25&end_date=2026-12-27")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["destination_id"] == "darjeeling"
    assert data["recommended_action"] in ["CHANGE_DESTINATION", "CHANGE_DATES", "KEEP_DESTINATION"]
    assert len(data["alternative_destinations"]) > 0
    assert len(data["alternative_dates"]) > 0

    post_res = client.post(
        "/api/destinations/darjeeling/decision",
        json={
            "start_date": "2026-12-25",
            "end_date": "2026-12-27",
            "budget": "Moderate",
            "group_size": 2
        }
    )
    assert post_res.status_code == 200
    post_data = post_res.json()
    assert post_data["recommended_action"] == "CHANGE_DESTINATION"

def test_generate_itinerary():
    payload = {
        "destination_id": "kalimpong",
        "duration_days": 3,
        "traveler_type": "Couple",
        "pace": "Moderate",
        "interests": ["Nature", "Culture"],
        "budget_level": "Moderate"
    }
    res = client.post("/api/itinerary/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["days"]) in [2, 3]

def test_homestays_and_booking():
    res = client.get("/api/homestays?destination_id=kalimpong")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1

    booking_payload = {
        "homestay_id": data[0]["id"],
        "traveler_name": "Aarav Sharma",
        "traveler_phone": "+91 98765 43210",
        "traveler_email": "aarav.sharma@example.com",
        "emergency_contact": "+91 98111 22233",
        "check_in_date": "2026-10-12",
        "check_out_date": "2026-10-15",
        "number_of_guests": 2
    }
    b_res = client.post("/api/bookings", json=booking_payload)
    assert b_res.status_code == 200
    b_data = b_res.json()
    assert b_data["status"] == "CONFIRMED"
    assert "YS-BK-" in b_data["booking_id"]

def test_safety_sos():
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
