"""
Tests for GET /api/v1/homestays with destination_id filtering and verification enforcement.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHomestayListingEndpoint:
    """Tests for GET /api/v1/homestays"""

    def test_lists_only_verified_homestays(self):
        """Endpoint must never return unverified homestays."""
        response = client.get("/api/homestays")
        assert response.status_code == 200
        homestays = response.json()
        for hs in homestays:
            assert hs["verified"] is True, (
                f"Unverified homestay {hs['id']} leaked into the response"
            )

    def test_returns_list(self):
        """Response must be a list (even if empty)."""
        response = client.get("/api/homestays")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_filter_by_destination_id_returns_only_that_destination(self):
        """All returned homestays must belong to the requested destination."""
        dest = "kalimpong"
        response = client.get(f"/api/homestays?destination_id={dest}")
        assert response.status_code == 200
        homestays = response.json()
        for hs in homestays:
            assert hs["destination_id"] == dest, (
                f"Homestay {hs['id']} has destination_id={hs['destination_id']!r}, "
                f"expected {dest!r}"
            )

    def test_filter_by_destination_id_excludes_other_destinations(self):
        """Homestays from other destinations must NOT appear when filtering."""
        all_resp = client.get("/api/homestays")
        all_homestays = all_resp.json()
        if len(all_homestays) == 0:
            pytest.skip("No verified homestays in seed data — cannot test exclusion")

        # Find a destination that exists in seed data
        dest = all_homestays[0]["destination_id"]
        # Find any other destination present
        other_dests = {hs["destination_id"] for hs in all_homestays if hs["destination_id"] != dest}
        if not other_dests:
            pytest.skip("Only one destination present in seed data")

        response = client.get(f"/api/homestays?destination_id={dest}")
        assert response.status_code == 200
        filtered = response.json()
        returned_dests = {hs["destination_id"] for hs in filtered}
        assert returned_dests.issubset({dest}), (
            f"Filter leaked homestays from other destinations: {returned_dests - {dest}}"
        )

    def test_filter_by_nonexistent_destination_returns_empty(self):
        """A filter for a destination with no homestays returns an empty list."""
        response = client.get("/api/homestays?destination_id=nonexistent_xyz")
        assert response.status_code == 200
        assert response.json() == []

    def test_destination_id_filter_is_case_insensitive(self):
        """destination_id filter must work regardless of casing."""
        lower = client.get("/api/homestays?destination_id=kalimpong").json()
        upper = client.get("/api/homestays?destination_id=KALIMPONG").json()
        # At minimum both calls must return only valid data; IDs must match
        assert {hs["id"] for hs in lower} == {hs["id"] for hs in upper}

    def test_response_schema_has_required_fields(self):
        """Each homestay object must have the core required fields."""
        response = client.get("/api/homestays")
        assert response.status_code == 200
        required_fields = {"id", "destination_id", "title", "price_per_night_inr", "verified"}
        for hs in response.json():
            missing = required_fields - hs.keys()
            assert not missing, f"Homestay {hs.get('id')} is missing fields: {missing}"


class TestHomestayDestinationIntegration:
    """Tests verifying destination-linked homestay access patterns."""

    def test_each_verified_homestay_has_destination_id(self):
        """Every homestay returned must declare a non-empty destination_id."""
        response = client.get("/api/homestays")
        assert response.status_code == 200
        for hs in response.json():
            assert hs.get("destination_id"), (
                f"Homestay {hs['id']} is missing destination_id"
            )

    def test_booking_uses_correct_destination(self):
        """A booking for a kalimpong homestay must record kalimpong destination_id."""
        # Find a kalimpong homestay first
        hs_resp = client.get("/api/homestays?destination_id=kalimpong")
        kalimpong_homestays = hs_resp.json()
        if not kalimpong_homestays:
            pytest.skip("No kalimpong homestays in seed data")

        hs_id = kalimpong_homestays[0]["id"]
        payload = {
            "homestay_id": hs_id,
            "traveler_name": "Test Traveler",
            "traveler_phone": "+91 9000000000",
            "traveler_email": "test@example.com",
            "emergency_contact": "+91 9111111111",
            "check_in_date": "2026-10-10",
            "check_out_date": "2026-10-13",
            "number_of_guests": 2,
        }
        booking_resp = client.post("/api/bookings", json=payload)
        assert booking_resp.status_code == 200
        booking = booking_resp.json()
        assert booking["homestay"]["destination_id"] == "kalimpong"

    def test_trip_details_returns_correct_destination(self):
        """Trip details must reflect the destination of the underlying booking."""
        hs_resp = client.get("/api/homestays?destination_id=kalimpong")
        kalimpong_homestays = hs_resp.json()
        if not kalimpong_homestays:
            pytest.skip("No kalimpong homestays in seed data")

        hs_id = kalimpong_homestays[0]["id"]
        payload = {
            "homestay_id": hs_id,
            "traveler_name": "Journey Tester",
            "traveler_phone": "+91 9222222222",
            "traveler_email": "journey@example.com",
            "emergency_contact": "+91 9333333333",
            "check_in_date": "2026-11-01",
            "check_out_date": "2026-11-04",
            "number_of_guests": 1,
        }
        booking = client.post("/api/bookings", json=payload).json()
        booking_id = booking["booking_id"]

        trip_resp = client.get(f"/api/trips/{booking_id}")
        assert trip_resp.status_code == 200
        trip = trip_resp.json()
        assert trip["destination_id"] == "kalimpong"
