"""
Unit and Integration Tests for Milestone 5: Production Data + Trust Layer.
Verifies:
- Observation normalization and schema
- Provider modes (MOCK, REAL, CACHED)
- Weather provider fallback
- Yatri network booking occupancy calculation
- Search demand leading indicator
- Event overlap and holiday periods
- Confidence engine evaluation
- Missing signals dynamic weight re-normalization
- Evidence API
- Forecast performance and provider status APIs
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.database import Base, engine
from app.models.entities import DestinationModel, CrowdObservationModel
from app.models.observation import (
    SignalType, ProviderMode, DataQuality, Observation,
    PressureEvidenceResponse, ProviderStatus, ForecastPerformance
)
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
from app.services.data_sources.weather_real_provider import WeatherProviderAdapter
from app.services.confidence_engine import confidence_engine
from app.services.forecast_accuracy_engine import forecast_accuracy_engine
from app.services.crowd_engine_v2 import crowd_engine_v2

client = TestClient(app)


# 1. Database Schema & Tables Test
def test_database_entities_registered():
    """Verify all 16 core entities are registered in SQLAlchemy metadata."""
    tables = list(Base.metadata.tables.keys())
    assert "destinations" in tables
    assert "attractions" in tables
    assert "hosts" in tables
    assert "homestays" in tables
    assert "experiences" in tables
    assert "bookings" in tables
    assert "availability" in tables
    assert "crowd_observations" in tables
    assert "crowd_predictions" in tables
    assert "weather_observations" in tables
    assert "traffic_observations" in tables
    assert "demand_observations" in tables
    assert "events" in tables
    assert "holidays" in tables
    assert "interventions" in tables
    assert "safety_incidents" in tables
    assert len(tables) >= 16


# 2. Observation Model & Normalization Test
def test_observation_normalization():
    """Verify Observation enforces 0-100 bounds and valid attributes."""
    obs = Observation(
        destination_id="darjeeling",
        signal_type=SignalType.HISTORICAL_FOOTFALL,
        raw_value=12500.0,
        normalized_value=92.5,
        unit="daily_footfall",
        source="MOCK_HISTORICAL",
        provider_mode=ProviderMode.MOCK,
        confidence=0.90,
        data_quality=DataQuality.HIGH
    )
    assert obs.normalized_value == 92.5
    assert 0.0 <= obs.normalized_value <= 100.0
    assert obs.provider_mode == ProviderMode.MOCK
    assert obs.signal_type == SignalType.HISTORICAL_FOOTFALL


# 3. Provider Modes Support (MOCK, REAL, CACHED)
def test_provider_modes():
    """Verify providers return valid modes and never mislabel MOCK as LIVE."""
    for prov in [
        tourism_data_provider,
        accommodation_data_provider,
        booking_demand_provider,
        search_demand_provider,
        event_data_provider,
        holiday_data_provider,
        traffic_data_provider,
        weather_data_provider
    ]:
        mode = prov.get_mode()
        assert mode in ("MOCK", "REAL", "CACHED")
        reading = prov.get_reading("darjeeling")
        # Ensure MOCK mode does not label source as LIVE
        if mode == "MOCK":
            assert not reading.source.startswith("LIVE")


# 4. Weather Provider Fallback Test
def test_weather_provider_fallback_without_key():
    """When OPENWEATHER_API_KEY is not provided, weather provider falls back cleanly to mock."""
    adapter = WeatherProviderAdapter()
    reading = adapter.get_reading("darjeeling")
    assert isinstance(reading, DataSourceReading)
    assert reading.available is True
    assert 0.0 <= reading.value <= 100.0
    assert reading.provider_mode == "MOCK"
    assert "Visibility" in reading.notes or "fallback" in reading.notes.lower()


# 5. Yatri Network Accommodation Occupancy Test
def test_yatri_network_accommodation_occupancy():
    """Verify platform occupancy calculation explicitly identifies as Yatri Setu network."""
    occ = accommodation_data_provider.get_platform_occupancy("darjeeling")
    assert occ["destination_id"] == "darjeeling"
    assert occ["total_capacity"] > 0
    assert occ["occupied_capacity"] > 0
    assert occ["occupancy_percent"] > 0
    assert occ["source_label"] == "Yatri Setu network occupancy"
    assert occ["is_nationwide"] is False

    reading = accommodation_data_provider.get_reading("darjeeling")
    assert "Yatri Setu network occupancy" in reading.source or "Yatri Setu network occupancy" in reading.notes


# 6. Search Demand Leading Indicator Test
def test_search_demand_leading_indicator():
    """Verify search demand tracks query metrics and explicitly labels leading indicator intent."""
    metrics = search_demand_provider.get_demand_metrics("darjeeling")
    assert metrics["destination_id"] == "darjeeling"
    assert metrics["search_count"] > 0
    assert metrics["unique_searchers"] > 0
    assert metrics["booking_conversion"] > 0
    assert metrics["is_leading_indicator"] is True
    assert metrics["trend"] in ("RISING", "STABLE", "DECLINING")

    reading = search_demand_provider.get_reading("darjeeling")
    assert "leading indicator" in reading.notes.lower()


# 7. Confidence Engine Calculation Test
def test_confidence_calculation_full_vs_degraded():
    """Verify confidence drops and data_quality degrades when signals are missing."""
    # Full 8 signals
    full_readings = [
        DataSourceReading(value=75.0, available=True, confidence=0.9, provider_mode="MOCK"),
        DataSourceReading(value=72.0, available=True, confidence=0.9, provider_mode="MOCK"),
        DataSourceReading(value=70.0, available=True, confidence=0.9, provider_mode="MOCK"),
        DataSourceReading(value=68.0, available=True, confidence=0.88, provider_mode="MOCK"),
        DataSourceReading(value=74.0, available=True, confidence=0.92, provider_mode="MOCK"),
        DataSourceReading(value=70.0, available=True, confidence=0.95, provider_mode="MOCK"),
        DataSourceReading(value=75.0, available=True, confidence=0.90, provider_mode="MOCK"),
        DataSourceReading(value=72.0, available=True, confidence=0.90, provider_mode="MOCK"),
    ]
    full_eval = confidence_engine.calculate_confidence(full_readings, total_expected=8)
    assert full_eval["signals_available"] == 8
    assert full_eval["confidence"] >= 0.80
    assert full_eval["data_quality"] in (DataQuality.HIGH.value, DataQuality.MEDIUM.value)

    # Degraded (only 3 signals available)
    degraded_readings = [
        DataSourceReading(value=75.0, available=True, confidence=0.9, provider_mode="MOCK"),
        DataSourceReading(value=72.0, available=True, confidence=0.9, provider_mode="MOCK"),
        DataSourceReading(value=70.0, available=True, confidence=0.9, provider_mode="MOCK"),
        DataSourceReading(value=50.0, available=False, confidence=0.0, provider_mode="MOCK"),
        DataSourceReading(value=50.0, available=False, confidence=0.0, provider_mode="MOCK"),
        DataSourceReading(value=50.0, available=False, confidence=0.0, provider_mode="MOCK"),
        DataSourceReading(value=50.0, available=False, confidence=0.0, provider_mode="MOCK"),
        DataSourceReading(value=50.0, available=False, confidence=0.0, provider_mode="MOCK"),
    ]
    degraded_eval = confidence_engine.calculate_confidence(degraded_readings, total_expected=8)
    assert degraded_eval["signals_available"] == 3
    assert degraded_eval["confidence"] < full_eval["confidence"]
    assert degraded_eval["data_quality"] in (DataQuality.LOW.value, DataQuality.DEGRADED.value)


# 8. Dynamic Weight Re-normalization Test
def test_dynamic_weight_renormalization():
    """Verify that when signals are missing, available weights are dynamically re-scaled to sum to 1.0."""
    # Test with custom weights where some signals are forced offline
    custom_weights = {
        "historical_footfall": 0.50,
        "traffic_pressure": 0.50
    }
    resp = crowd_engine_v2.calculate_pressure("darjeeling", custom_weights=custom_weights)
    assert resp.signals_available == 2
    # Check that effective weights of active signals sum to 1.0
    effective_weights = sum(s.weight for s in resp.signals)
    assert pytest.approx(effective_weights, 0.001) == 1.0


# 9. Evidence API Endpoint Test
def test_evidence_api_endpoint():
    """Verify GET /api/destinations/{id}/pressure/evidence returns full audit trail."""
    response = client.get("/api/destinations/darjeeling/pressure/evidence")
    assert response.status_code == 200
    data = response.json()
    assert data["destination_id"] == "darjeeling"
    assert "pressure_score" in data
    assert "confidence_score" in data
    assert "data_quality" in data
    assert len(data["signals"]) == 8
    # Check signal fields
    first_sig = data["signals"][0]
    assert "raw_value" in first_sig
    assert "normalized_value" in first_sig
    assert "weight" in first_sig
    assert "weighted_contribution" in first_sig
    assert "provider_mode" in first_sig
    assert first_sig["provider_mode"] in ("MOCK", "REAL", "CACHED")


# 10. Forecast Performance Endpoint Test
def test_forecast_performance_api_endpoint():
    """Verify GET /api/admin/forecast-performance returns MAE, RMSE, and directional accuracy."""
    response = client.get("/api/admin/forecast-performance")
    assert response.status_code == 200
    data = response.json()
    assert "mae" in data
    assert "rmse" in data
    assert "directional_accuracy_percent" in data
    assert data["mae"] > 0
    assert data["rmse"] > 0
    assert 0.0 <= data["directional_accuracy_percent"] <= 100.0
    assert len(data["evaluated_destinations"]) > 0


# 11. Providers Status Endpoint Test
def test_providers_status_api_endpoint():
    """Verify GET /api/admin/providers returns operational status of all 8 providers."""
    response = client.get("/api/admin/providers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8
    for prov in data:
        assert prov["status"] == "ONLINE"
        assert prov["mode"] in ("MOCK", "REAL", "CACHED")
        assert prov["weight_percent"] > 0
        assert "reliability_score" in prov
