import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.services.traffic.provider import (
    TomTomTrafficProvider,
    DemoTrafficProvider,
    UnavailableTrafficProvider,
)
from app.services.traffic.service import TrafficService
from app.services.traffic.schemas import DestinationTrafficSummary

client = TestClient(app)


def test_successful_tomtom_response_yields_real_provenance():
    """Verify successful TomTom response yields REAL — TOMTOM TRAFFIC provenance."""
    provider = TomTomTrafficProvider(api_key="valid_32_character_tomtom_key_123")
    service = TrafficService(provider=provider)

    mock_summary = {
        "lengthInMeters": 54000,
        "travelTimeInSeconds": 7200,
        "trafficDelayInSeconds": 360,
        "noTrafficTravelTimeInSeconds": 6840,
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"routes": [{"summary": mock_summary}]}

    with patch("httpx.Client.get", return_value=mock_resp):
        summary = service.get_traffic("darjeeling")
        assert summary.provider_mode == "REAL"
        assert summary.provenance_label == "REAL — TOMTOM TRAFFIC"
        assert summary.source == "TOMTOM_LIVE_TRAFFIC"
        assert summary.cache_status == "LIVE"
        assert summary.data_quality == "HIGH"
        assert summary.average_travel_time_ratio >= 1.0


def test_tomtom_http_failure_yields_safe_fallback():
    """Verify TomTom HTTP failure triggers safe fallback with DEMO or UNAVAILABLE provenance."""
    provider = TomTomTrafficProvider(api_key="valid_32_character_tomtom_key_123")
    service = TrafficService(provider=provider)

    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_resp.text = "Service Unavailable"

    with patch("httpx.Client.get", return_value=mock_resp):
        summary = service.get_traffic("darjeeling")
        # Must NOT be labeled as REAL
        assert summary.provider_mode != "REAL"
        assert summary.provider_mode in ("DEMO", "UNAVAILABLE")
        assert "DEMO" in summary.provenance_label or "UNAVAILABLE" in summary.provenance_label
        assert summary.provenance_label in ("DEMO MODE — SYNTHETIC DATA", "UNAVAILABLE — SAFE FALLBACK")
        assert summary.data_quality == "DEGRADED"


def test_malformed_tomtom_response_yields_safe_fallback():
    """Verify malformed TomTom JSON triggers safe fallback without crashing."""
    provider = TomTomTrafficProvider(api_key="valid_32_character_tomtom_key_123")
    service = TrafficService(provider=provider)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"routes": []}  # empty routes list

    with patch("httpx.Client.get", return_value=mock_resp):
        summary = service.get_traffic("darjeeling")
        assert summary.provider_mode != "REAL"
        assert summary.provenance_label == "DEMO MODE — SYNTHETIC DATA"
        assert summary.data_quality == "DEGRADED"


def test_stale_demo_cache_is_never_presented_as_real():
    """Verify that fallback demo data is never saved into real cache or labeled REAL."""
    provider = TomTomTrafficProvider(api_key="valid_32_character_tomtom_key_123")
    service = TrafficService(provider=provider)

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("httpx.Client.get", return_value=mock_resp):
        # 1st call fails and returns demo fallback
        first_call = service.get_traffic("darjeeling")
        assert first_call.provider_mode == "DEMO"
        assert first_call.provenance_label == "DEMO MODE — SYNTHETIC DATA"
        # Crucial check: demo fallback is NOT cached in service._cache
        assert "darjeeling" not in service._cache

        # 2nd call also fails and returns demo fallback
        second_call = service.get_traffic("darjeeling")
        assert second_call.provider_mode == "DEMO"
        assert second_call.provenance_label == "DEMO MODE — SYNTHETIC DATA"
        assert "REAL" not in second_call.provenance_label


def test_real_cache_hit_retains_real_provenance():
    """Verify cached real observations retain REAL provenance and report CACHED status."""
    provider = TomTomTrafficProvider(api_key="valid_32_character_tomtom_key_123")
    service = TrafficService(provider=provider)

    mock_summary = {
        "lengthInMeters": 54000,
        "travelTimeInSeconds": 7000,
        "trafficDelayInSeconds": 100,
        "noTrafficTravelTimeInSeconds": 6900,
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"routes": [{"summary": mock_summary}]}

    with patch("httpx.Client.get", return_value=mock_resp):
        live_obs = service.get_traffic("darjeeling")
        assert live_obs.cache_status == "LIVE"
        assert live_obs.provider_mode == "REAL"

    # Second call without network patch — served directly from cache
    cached_obs = service.get_traffic("darjeeling")
    assert cached_obs.cache_status == "CACHED"
    assert cached_obs.provider_mode == "REAL"
    assert "REAL" in cached_obs.provenance_label


def test_health_status_reflects_actual_provider_availability():
    """Verify /api/health?detailed=true tests connectivity rather than just key existence."""
    from app.services.traffic.service import traffic_service

    # Case 1: TomTom is reachable
    mock_probe_200 = MagicMock()
    mock_probe_200.status_code = 200

    with patch.object(traffic_service._provider, "check_connectivity", return_value=True):
        res = client.get("/api/health?detailed=true")
        assert res.status_code == 200
        data = res.json()
        assert data["providers"]["traffic"]["available"] is True
        assert data["providers"]["traffic"]["provenance"] == "REAL — TOMTOM TRAFFIC"

    # Case 2: TomTom probe fails (e.g. 401 Unauthorized or network down)
    with patch.object(traffic_service._provider, "check_connectivity", return_value=False):
        res = client.get("/api/health?detailed=true")
        assert res.status_code == 200
        data = res.json()
        assert data["providers"]["traffic"]["available"] is False
        assert data["providers"]["traffic"]["mode"] == "UNAVAILABLE"
        assert data["providers"]["traffic"]["provenance"] == "UNAVAILABLE — SAFE FALLBACK"
