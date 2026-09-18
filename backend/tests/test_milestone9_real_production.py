import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.traffic.provider import (
    TomTomTrafficProvider,
    DemoTrafficProvider,
    UnavailableTrafficProvider,
)
from app.services.traffic.service import TrafficService
from app.services.crowd_engine import (
    compute_dynamic_crowd_factors,
    calculate_crowd_score,
    _get_calendar_season_factors,
)

client = TestClient(app)


def test_tomtom_traffic_provider_missing_key():
    """Verify TomTomTrafficProvider raises RuntimeError when no API key is supplied."""
    provider = TomTomTrafficProvider(api_key=None)
    with pytest.raises(RuntimeError) as excinfo:
        provider.fetch_traffic("darjeeling")
    assert "TomTom traffic provider API key is not configured" in str(excinfo.value)


def test_tomtom_traffic_provider_parses_real_response():
    """Verify TomTomTrafficProvider accurately parses TomTom Routing API JSON."""
    provider = TomTomTrafficProvider(api_key="test_tomtom_key")
    
    mock_tomtom_response = {
        "routes": [
            {
                "summary": {
                    "lengthInMeters": 68000,
                    "travelTimeInSeconds": 8500,
                    "trafficDelayInSeconds": 1300,
                    "noTrafficTravelTimeInSeconds": 7200,
                },
                "legs": [
                    {
                        "points": [
                            {"latitude": 26.7271, "longitude": 88.3953},
                            {"latitude": 27.0410, "longitude": 88.2663},
                        ]
                    }
                ]
            }
        ]
    }
    
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_tomtom_response
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        
        result = provider.fetch_traffic("darjeeling")
        
        assert result.provider_mode == "REAL"
        assert result.provenance_label == "REAL — TOMTOM TRAFFIC"
        assert result.source == "TOMTOM_LIVE_TRAFFIC"
        assert result.average_travel_time_ratio >= 1.0
        assert len(result.critical_routes) >= 1
        first_route = result.critical_routes[0]
        assert first_route.current_travel_time_min > 0
        assert first_route.road_status in ("CLEAR", "SLOW", "RESTRICTED", "CLOSED")


def test_traffic_service_never_labels_fallback_as_real():
    """Verify TrafficService falling back from TomTom to Demo preserves DEMO provenance."""
    # Initialize TrafficService with TomTom provider that has no key
    service = TrafficService(provider=TomTomTrafficProvider(api_key=None))
    
    summary = service.get_traffic("darjeeling")
    
    # Must NOT be labeled as REAL
    assert summary.provider_mode != "REAL"
    assert "REAL" not in summary.provenance_label or "DEMO" in summary.provenance_label
    assert summary.provenance_label == "DEMO MODE — SYNTHETIC DATA"


def test_demo_and_unavailable_providers_provenance():
    """Verify Demo and Unavailable providers explicitly declare non-real provenance."""
    demo = DemoTrafficProvider().fetch_traffic("kalimpong")
    assert demo.provider_mode == "DEMO"
    assert demo.provenance_label == "DEMO MODE — SYNTHETIC DATA"

    unavail = UnavailableTrafficProvider().fetch_traffic("kalimpong")
    assert unavail.provider_mode == "UNAVAILABLE"
    assert unavail.provenance_label == "UNAVAILABLE — SAFE FALLBACK"


def test_calendar_season_factors():
    """Verify calendar and seasonality factors calculate realistic multipliers."""
    # Month 5 (May - peak season)
    factors_may = _get_calendar_season_factors(5, 5)  # Saturday in May
    assert factors_may["seasonal_factor"] > 1.0
    assert factors_may["weekend_factor"] > 1.0

    # Month 7 (July - monsoon low season)
    factors_july = _get_calendar_season_factors(7, 2)  # Tuesday in July
    assert factors_july["seasonal_factor"] < 1.0
    assert factors_july["weekend_factor"] == 1.0


def test_compute_dynamic_crowd_factors_provenance():
    """Verify dynamic crowd factor calculation computes factors and provides valid provenance."""
    factors, meta = compute_dynamic_crowd_factors("darjeeling")
    assert isinstance(factors, dict)
    assert "historical_footfall" in factors
    assert "booking_density" in factors
    assert "traffic_factor" in factors
    mode = meta.get("provider_mode")
    provenance = meta.get("provenance_label")
    assert mode in ("REAL", "MIXED", "DEMO")
    assert ("REAL" in provenance or "MIXED" in provenance or "DEMO" in provenance)


def test_health_detailed_endpoint_includes_all_providers():
    """Verify /api/health?detailed=true includes routing, weather, and traffic provider details."""
    response = client.get("/api/health?detailed=true")
    assert response.status_code == 200
    data = response.json()
    
    assert "routing" in data
    assert "weather" in data
    assert "traffic" in data
    assert "providers" in data
    
    # Traffic block
    traffic_info = data["traffic"]
    assert "provider" in traffic_info
    assert "mode" in traffic_info
    assert "provenance" in traffic_info
    
    # Routing block
    routing_info = data["routing"]
    assert "provider" in routing_info
    assert "provenance" in routing_info
    
    # Weather block
    weather_info = data["weather"]
    assert "provider" in weather_info
    assert "provenance" in weather_info


def test_crowd_endpoint_includes_provenance():
    """Verify destination crowd endpoint returns provenance metadata."""
    response = client.get("/api/destinations/darjeeling/crowd")
    assert response.status_code == 200
    data = response.json()
    
    assert "crowd_score" in data
    assert "crowd_level" in data
    assert "factors" in data
    assert "provenance_label" in data
    assert "provider_mode" in data
    assert data["provider_mode"] in ("REAL", "MIXED", "DEMO")
