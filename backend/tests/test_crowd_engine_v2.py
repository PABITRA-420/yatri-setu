"""
Tests for Crowd Engine V2, Data Source Providers, and Admin Command Center.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.services.crowd_engine_v2 import crowd_engine_v2, CrowdEngineV2, DEFAULT_V2_WEIGHTS
from app.services.events_engine import events_engine
from app.services.holiday_engine import holiday_engine
from app.services.data_sources import (
    tourism_data_provider,
    accommodation_data_provider,
    booking_demand_provider,
    search_demand_provider,
    event_data_provider,
    holiday_data_provider,
    traffic_data_provider,
    weather_data_provider,
    DataSourceReading
)

client = TestClient(app)


def test_v2_weights_sum_to_one():
    total = sum(DEFAULT_V2_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001
    assert len(DEFAULT_V2_WEIGHTS) == 8


def test_v2_invalid_weights_raise_error():
    invalid_weights = {"historical_footfall": 0.50}  # sums to 0.50
    with pytest.raises(ValueError) as exc:
        CrowdEngineV2(weights=invalid_weights)
    assert "must sum to 1.0" in str(exc.value)


def test_all_eight_providers_respond():
    dest = "darjeeling"
    providers = [
        tourism_data_provider,
        accommodation_data_provider,
        booking_demand_provider,
        search_demand_provider,
        event_data_provider,
        holiday_data_provider,
        traffic_data_provider,
        weather_data_provider
    ]
    for p in providers:
        reading = p.get_reading(dest)
        assert isinstance(reading, DataSourceReading)
        assert 0.0 <= reading.value <= 100.0
        assert 0.0 <= reading.confidence <= 1.0
        assert reading.available is True
        assert reading.source.startswith("MOCK") or "TOMTOM" in reading.source or "OPENWEATHER" in reading.source or reading.provider_mode in ("REAL", "DEMO")


def test_darjeeling_high_pressure_profile():
    res = crowd_engine_v2.calculate_pressure("darjeeling")
    assert res.destination_id == "darjeeling"
    assert res.pressure_score >= 60.0
    assert res.pressure_level in ("HIGH", "CRITICAL", "MODERATE")
    assert res.signals_available == 8
    assert res.confidence_score >= 0.85
    assert len(res.signals) == 8


def test_rural_destinations_low_pressure():
    for rural_dest in ["lava", "lolegaon", "rishop"]:
        res = crowd_engine_v2.calculate_pressure(rural_dest)
        assert res.pressure_score < 50.0
        assert res.pressure_level in ("LOW", "MODERATE")
        assert res.carrying_capacity_percent < 50.0


def test_missing_provider_graceful_handling():
    """Engine gracefully falls back if a provider fails or is unconfigured."""
    engine = CrowdEngineV2()
    # Mock a broken provider
    class FailingProvider:
        def is_available(self):
            return False
        def get_reading(self, *args):
            raise RuntimeError("Provider down")

    engine.providers["weather_pressure"] = FailingProvider()
    res = engine.calculate_pressure("darjeeling")
    assert res.pressure_score > 0.0
    assert res.signals_available == 7  # 7 out of 8 available
    weather_sig = next(s for s in res.signals if s.signal_key == "weather_pressure")
    assert weather_sig.available is False
    assert weather_sig.confidence == 0.0
    assert weather_sig.value == 50.0  # neutral fallback


def test_events_engine_active_events():
    # Darjeeling carnival date: Nov 25
    nov_date = date(2026, 11, 25)
    res = events_engine.calculate_event_pressure("darjeeling", nov_date)
    assert res["score"] >= 80.0
    assert len(res["active_events"]) >= 1
    assert any("Carnival" in e["name"] for e in res["active_events"])


def test_holiday_engine_long_weekend_detection():
    # Oct 2, 2026 is Friday (Gandhi Jayanti) -> creates a long weekend!
    gandhi_jayanti = date(2026, 10, 2)
    res = holiday_engine.calculate_holiday_pressure(gandhi_jayanti)
    assert res["is_holiday"] is True
    assert res["score"] >= 80.0


def test_pressure_forecast():
    forecast = crowd_engine_v2.calculate_pressure_forecast("darjeeling", days=7)
    assert forecast.destination_id == "darjeeling"
    assert len(forecast.forecast_days) == 7
    assert forecast.current_pressure >= 60.0
    for day in forecast.forecast_days:
        assert 0.0 <= day.predicted_pressure <= 100.0
        assert day.confidence_score > 0.50
        assert day.key_driver != ""


def test_intervention_simulation():
    result = crowd_engine_v2.simulate_intervention(
        destination_id="darjeeling",
        intervention_type="entry_quota",
        intensity_percent=30.0
    )
    assert result.destination_id == "darjeeling"
    assert result.simulated_pressure < result.original_pressure
    assert result.pressure_reduction_percent > 15.0
    assert result.redirected_tourists_count > 0
    assert len(result.beneficiary_destinations) >= 2
    assert result.total_rural_revenue_generated_inr > 0.0
    assert result.is_simulation is True


# API Endpoint Integration Tests

def test_api_destination_pressure():
    res = client.get("/api/destinations/darjeeling/pressure")
    assert res.status_code == 200
    data = res.json()
    assert data["destination_id"] == "darjeeling"
    assert data["signals_available"] == 8
    assert len(data["signals"]) == 8
    assert "carrying_capacity_percent" in data
    assert "advisory" in data


def test_api_destination_forecast():
    res = client.get("/api/destinations/darjeeling/pressure/forecast?days=5")
    assert res.status_code == 200
    data = res.json()
    assert data["destination_id"] == "darjeeling"
    assert len(data["forecast_days"]) == 5
    assert data["trend"] in ("RISING", "FALLING", "STABLE")


def test_api_admin_command_center():
    res = client.get("/api/admin/command-center")
    assert res.status_code == 200
    data = res.json()
    assert data["total_destinations_monitored"] >= 6
    assert data["total_active_signals"] == 8
    assert len(data["destinations"]) >= 6
    assert len(data["flow_summary"]) >= 1


def test_api_admin_destinations_pressure():
    res = client.get("/api/admin/destinations/pressure")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 6
    dest_ids = [d["destination_id"] for d in data]
    assert "darjeeling" in dest_ids
    assert "lava" in dest_ids


def test_api_admin_flow():
    res = client.get("/api/admin/flow")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    flow0 = data[0]
    assert flow0["origin_destination_id"] == "darjeeling"
    assert flow0["economic_impact_inr_7d"] > 0


def test_api_admin_intervention_simulation_post():
    payload = {
        "destination_id": "darjeeling",
        "intervention_type": "shuttle_diversion",
        "intensity_percent": 25.0
    }
    res = client.post("/api/admin/intervention-simulation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["destination_id"] == "darjeeling"
    assert data["simulated_pressure"] < data["original_pressure"]
    assert data["total_rural_revenue_generated_inr"] > 0
    assert len(data["beneficiary_destinations"]) > 0


def test_api_admin_intervention_simulation_get():
    res = client.get("/api/admin/intervention-simulation?destination_id=darjeeling&intervention_type=entry_quota&intensity_percent=20")
    assert res.status_code == 200
    data = res.json()
    assert data["destination_id"] == "darjeeling"
    assert data["is_simulation"] is True
